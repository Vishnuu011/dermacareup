import stripe
from src.config.config import settings
from src.logger.custom_logger import logger
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentHandler:
    """Handles all Stripe payment operations"""
    
    @staticmethod
    def create_payment_intent(
        amount: int,
        currency: str = "usd",
        description: str = "",
        customer_email: str = "",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent
        
        Args:
            amount: Amount in cents (e.g., 1000 for $10.00)
            currency: Currency code (default: usd)
            description: Payment description
            customer_email: Customer email
            metadata: Additional metadata to store with the payment
        
        Returns:
            Payment intent object
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                description=description,
                receipt_email=customer_email,
                metadata=metadata or {}
            )
            logger.info(f"Created payment intent: {intent['id']}")
            return {
                "success": True,
                "client_secret": intent['client_secret'],
                "payment_intent_id": intent['id'],
                "amount": intent['amount'],
                "currency": intent['currency'],
                "status": intent['status']
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a payment intent status
        
        Args:
            payment_intent_id: Stripe payment intent ID
        
        Returns:
            Payment intent details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "success": True,
                "payment_intent_id": intent['id'],
                "status": intent['status'],
                "amount": intent['amount'],
                "currency": intent['currency'],
                "client_secret": intent['client_secret']
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def create_subscription(
        customer_email: str,
        price_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe subscription
        
        Args:
            customer_email: Customer email
            price_id: Stripe price ID for the subscription plan
            metadata: Additional metadata
        
        Returns:
            Subscription details
        """
        try:
            # Create or get customer
            customers = stripe.Customer.list(email=customer_email, limit=1)
            
            if customers.data:
                customer_id = customers.data[0].id
            else:
                customer = stripe.Customer.create(email=customer_email)
                customer_id = customer.id
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {}
            )
            
            logger.info(f"Created subscription: {subscription['id']}")
            return {
                "success": True,
                "subscription_id": subscription['id'],
                "customer_id": customer_id,
                "status": subscription['status'],
                "current_period_start": subscription['current_period_start'],
                "current_period_end": subscription['current_period_end']
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a Stripe subscription
        
        Args:
            subscription_id: Stripe subscription ID
        
        Returns:
            Cancellation confirmation
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled subscription: {subscription_id}")
            return {
                "success": True,
                "subscription_id": subscription['id'],
                "status": subscription['status'],
                "cancelled_at": subscription['canceled_at']
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature
        
        Args:
            body: Raw request body
            signature: Stripe signature header
        
        Returns:
            Verification result and event data
        """
        try:
            event = stripe.Webhook.construct_event(
                body, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            logger.info(f"Verified webhook event: {event['type']}")
            return {
                "success": True,
                "event": event
            }
        except ValueError as e:
            logger.error(f"Invalid webhook body: {str(e)}")
            return {
                "success": False,
                "error": "Invalid payload"
            }
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            return {
                "success": False,
                "error": "Invalid signature"
            }
    
    @staticmethod
    def create_payment_method(
        card_number: str,
        exp_month: int,
        exp_year: int,
        cvc: str
    ) -> Dict[str, Any]:
        """
        Create a payment method (card)
        
        Args:
            card_number: Card number
            exp_month: Expiration month
            exp_year: Expiration year
            cvc: Card verification code
        
        Returns:
            Payment method details
        """
        try:
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": card_number,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc,
                },
            )
            logger.info(f"Created payment method: {payment_method['id']}")
            return {
                "success": True,
                "payment_method_id": payment_method['id'],
                "card_last4": payment_method['card']['last4']
            }
        except stripe.error.CardError as e:
            logger.error(f"Card error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment method: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def retrieve_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Retrieve subscription details
        
        Args:
            subscription_id: Stripe subscription ID
        
        Returns:
            Subscription details
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "success": True,
                "subscription_id": subscription['id'],
                "status": subscription['status'],
                "customer_id": subscription['customer'],
                "current_period_start": subscription['current_period_start'],
                "current_period_end": subscription['current_period_end'],
                "items": subscription['items']['data']
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
