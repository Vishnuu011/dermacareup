from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from src.helpers.deps import (
    get_current_user,
    get_current_organization
)
from src.schema.Schemas import(
    SubscriptionCreate,
    SubscriptionResponse
)
from src.models.DatabaseModels import (
    SubscriptionsModel,
    UserModel,
    OrganizationModel
)
from src.helpers.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os, sys


subscription_router = APIRouter(
    prefix="/api/v1/subscriptions",
    tags=["subscriptions"]
)



@subscription_router.post("/choose-subscription", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: UserModel = Depends(get_current_user),
    current_organization: OrganizationModel = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    
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
        
    except Exception as e:
        print(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the subscription."
        )