from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Header
)

from src.helpers.deps import (
    get_current_user,
    get_current_organization
)
from src.helpers.stripe_utils import StripePaymentHandler
from src.schema.Schemas import(
    SubscriptionCreate,
    SubscriptionResponse,
    CreatePaymentIntentRequest,
    PaymentIntentResponse,
    StripeSubscriptionRequest,
    StripeSubscriptionResponse,
    UpdatePaymentStatusRequest,
    WebhookEventResponse,
    PaymentResponse,
    PaymentMethodRequest,
    PaymentMethodResponse
)
from src.models.DatabaseModels import (
    SubscriptionsModel,
    UserModel,
    OrganizationModel,
    PaymentsModel
)
from src.helpers.deps import get_db
from src.logger.custom_logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os, sys
from uuid import uuid4
from datetime import datetime


payment_router = APIRouter(
    prefix="/api/v1/payments",
    tags=["payments"]
)


@payment_router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription"""
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can create subscriptions."
            )
        
        if current_organization.org_id != subscription.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create subscriptions for your own organization."
            )
        
        new_subscription = SubscriptionsModel(
            organization_id=subscription.organization_id,
            plan_name=subscription.plan_name,
            scan_limit=subscription.scan_limit,
            price=subscription.price,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            status=subscription.status
        )
        db.add(new_subscription)
        await db.flush()
        await db.commit()
        await db.refresh(new_subscription)      
        return SubscriptionResponse(
            subscription_id=new_subscription.subscription_id,
            organization_id=new_subscription.organization_id,
            plan_name=new_subscription.plan_name,
            scan_limit=new_subscription.scan_limit,
            price=new_subscription.price,
            start_date=new_subscription.start_date,
            end_date=new_subscription.end_date,
            status=new_subscription.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the subscription."
        )


# ===================== STRIPE PAYMENT INTENT ENDPOINTS =====================

@payment_router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe payment intent for subscription payment
    This endpoint initializes a payment and returns a client secret for frontend processing
    """
    try:
        # Verify subscription exists if provided
        if request.subscription_id:
            query = select(SubscriptionsModel).where(
                SubscriptionsModel.subscription_id == str(request.subscription_id),
                SubscriptionsModel.organization_id == str(current_organization.org_id)
            )
            result = await db.execute(query)
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subscription not found"
                )
        
        # Create payment intent with Stripe
        stripe_response = StripePaymentHandler.create_payment_intent(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            customer_email=current_user.email,
            metadata={
                "organization_id": str(current_organization.org_id),
                "user_id": str(current_user.user_id),
                "subscription_id": str(request.subscription_id) if request.subscription_id else ""
            }
        )
        
        if not stripe_response.get("success"):
            logger.error(f"Stripe error: {stripe_response.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=stripe_response.get("error", "Failed to create payment intent")
            )
        
        return PaymentIntentResponse(
            success=True,
            client_secret=stripe_response["client_secret"],
            payment_intent_id=stripe_response["payment_intent_id"],
            amount=stripe_response["amount"],
            currency=stripe_response["currency"],
            status=stripe_response["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating payment intent"
        )


@payment_router.post("/confirm-payment")
async def confirm_payment(
    request: UpdatePaymentStatusRequest,
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm a payment after Stripe processing
    This should be called after the client side payment is confirmed
    """
    try:
        # Verify the payment intent with Stripe
        stripe_response = StripePaymentHandler.retrieve_payment_intent(
            request.stripe_payment_id
        )
        
        if not stripe_response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve payment status"
            )
        
        # Save payment record to database
        new_payment = PaymentsModel(
            payment_id=str(uuid4()),
            organization_id=str(current_organization.org_id),
            subscription_id=None,  # Will be set from request if needed
            stripe_payment_id=request.stripe_payment_id,
            amount=stripe_response["amount"],
            currency=stripe_response["currency"],
            payment_status=stripe_response["status"],
            payment_date=datetime.utcnow()
        )
        
        db.add(new_payment)
        await db.commit()
        await db.refresh(new_payment)
        
        logger.info(f"Payment confirmed: {new_payment.payment_id}")
        
        return {
            "success": True,
            "message": "Payment confirmed successfully",
            "payment_id": new_payment.payment_id,
            "status": new_payment.payment_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while confirming payment"
        )


@payment_router.get("/payment-status/{payment_intent_id}")
async def get_payment_status(
    payment_intent_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the status of a payment intent"""
    try:
        stripe_response = StripePaymentHandler.retrieve_payment_intent(payment_intent_id)
        
        if not stripe_response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve payment status"
            )
        
        return stripe_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred retrieving payment status"
        )


# ===================== STRIPE SUBSCRIPTION ENDPOINTS =====================

@payment_router.post("/create-stripe-subscription", response_model=StripeSubscriptionResponse)
async def create_stripe_subscription(
    request: StripeSubscriptionRequest,
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe recurring subscription
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can create subscriptions"
            )
        
        # Create Stripe subscription
        stripe_response = StripePaymentHandler.create_subscription(
            customer_email=current_user.email,
            price_id=request.price_id,
            metadata={
                "organization_id": str(current_organization.org_id),
                "plan_name": request.plan_name
            }
        )
        
        if not stripe_response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=stripe_response.get("error", "Failed to create subscription")
            )
        
        # Save subscription to database
        new_subscription = SubscriptionsModel(
            subscription_id=stripe_response["subscription_id"],
            organization_id=str(current_organization.org_id),
            plan_name=request.plan_name,
            scan_limit=request.scan_limit,
            price=0,  # Price is managed by Stripe
            status="active"
        )
        
        db.add(new_subscription)
        await db.commit()
        await db.refresh(new_subscription)
        
        logger.info(f"Stripe subscription created: {stripe_response['subscription_id']}")
        
        return StripeSubscriptionResponse(
            success=True,
            subscription_id=stripe_response["subscription_id"],
            customer_id=stripe_response["customer_id"],
            status=stripe_response["status"],
            current_period_start=stripe_response["current_period_start"],
            current_period_end=stripe_response["current_period_end"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Stripe subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating subscription"
        )


@payment_router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a Stripe subscription"""
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can cancel subscriptions"
            )
        
        # Cancel with Stripe
        stripe_response = StripePaymentHandler.cancel_subscription(subscription_id)
        
        if not stripe_response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=stripe_response.get("error", "Failed to cancel subscription")
            )
        
        # Update subscription status in database
        query = select(SubscriptionsModel).where(
            SubscriptionsModel.subscription_id == subscription_id,
            SubscriptionsModel.organization_id == str(current_organization.org_id)
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = "cancelled"
            await db.commit()
        
        logger.info(f"Subscription cancelled: {subscription_id}")
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully",
            "subscription_id": subscription_id,
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while cancelling subscription"
        )


# ===================== WEBHOOK ENDPOINT =====================

@payment_router.post("/webhook", response_model=WebhookEventResponse)
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(None)
):
    """
    Handle Stripe webhook events
    This endpoint processes events from Stripe (payment_intent.succeeded, subscription updates, etc.)
    """
    try:
        if not stripe_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )
        
        body = await request.body()
        
        # Verify webhook signature
        webhook_result = StripePaymentHandler.verify_webhook_signature(
            body, stripe_signature
        )
        
        if not webhook_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        event = webhook_result["event"]
        event_type = event["type"]
        
        # Handle different event types
        if event_type == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            logger.info(f"Payment succeeded: {payment_intent['id']}")
            
            # Update or create payment record
            metadata = payment_intent.get("metadata", {})
            
            try:
                payment_record = PaymentsModel(
                    payment_id=str(uuid4()),
                    organization_id=metadata.get("organization_id"),
                    subscription_id=metadata.get("subscription_id"),
                    stripe_payment_id=payment_intent["id"],
                    amount=payment_intent["amount"],
                    currency=payment_intent["currency"],
                    payment_status="succeeded",
                    payment_date=datetime.utcnow()
                )
                db.add(payment_record)
                await db.commit()
            except Exception as e:
                logger.error(f"Error saving payment record: {e}")
        
        elif event_type == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            logger.warning(f"Payment failed: {payment_intent['id']}")
        
        elif event_type == "customer.subscription.updated":
            subscription = event["data"]["object"]
            logger.info(f"Subscription updated: {subscription['id']}")
        
        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            logger.info(f"Subscription cancelled: {subscription['id']}")
        
        return WebhookEventResponse(
            success=True,
            message=f"Webhook processed: {event_type}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred handling webhook"
        )


# ===================== PAYMENT HISTORY =====================

@payment_router.get("/history")
async def get_payment_history(
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get payment history for the organization"""
    try:
        query = select(PaymentsModel).where(
            PaymentsModel.organization_id == str(current_organization.org_id)
        ).order_by(PaymentsModel.payment_date.desc())
        
        result = await db.execute(query)
        payments = result.scalars().all()
        
        return {
            "success": True,
            "total_payments": len(payments),
            "payments": [
                PaymentResponse(
                    payment_id=p.payment_id,
                    organization_id=p.organization_id,
                    subscription_id=p.subscription_id,
                    stripe_payment_id=p.stripe_payment_id,
                    amount=p.amount,
                    currency=p.currency,
                    payment_status=p.payment_status,
                    payment_date=p.payment_date
                ) for p in payments
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred retrieving payment history"
        )
