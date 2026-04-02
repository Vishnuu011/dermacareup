from fastapi import (
    APIRouter, 
    Depends, 
    status, 
    HTTPException
)

from fastapi.responses import JSONResponse
from src.helpers.deps import (
    get_current_user, 
    get_current_organization
)
from src.helpers.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    generate_password_reset_token
)

from src.schema.Schemas import (
    LoginResponse, 
    RegisterRequest, 
    RegisterResponse, 
    LoginRequest, 
    OrganizationResponse, 
    UserResponse, 
    AccountMeResponse,
    AccountUpdateRequest, 
    AccountUpdateResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse
)

from src.helpers.deps import get_db
from src.helpers.email_utils import send_password_reset_email
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.DatabaseModels import (
    UserModel, 
    OrganizationModel, 
    PasswordResetToken
)
from src.exceptions.custom_exception import (
    DatabaseException, 
    AuthenticationException
)
from datetime import timedelta, datetime
from src.helpers.deps import get_current_user
from src.logger.custom_logger import logger


auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"]
)



@auth_router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_orginisation_and_user(
    register_data: RegisterRequest,
    db : AsyncSession = Depends(get_db)

) -> RegisterResponse:
    
    try:
        logger.info(
            f"""Registration attempt for organization: {
                register_data.organization.name
            }, user: {register_data.user.email}"""
        )

        existing_org = await db.execute(
            select(
                OrganizationModel
            ).where(
                OrganizationModel.email == register_data.organization.email
            )
        )
        if existing_org.scalars().first():
            raise DatabaseException(
                "Organization with this email already exists"
            )
        
        existing_user = await db.execute(
            select(
                UserModel
            ).where(
                UserModel.email == register_data.user.email
            )
        )       

        if existing_user.scalars().first():
            raise DatabaseException(
                "User with this email already exists"
            )   

        create_org = OrganizationModel(
            name=register_data.organization.name,
            type=register_data.organization.type,
            email=register_data.organization.email,
            phone=register_data.organization.phone,
            address=register_data.organization.address
        ) 
        db.add(create_org)
        await db.flush()
        await db.commit()
        
        create_user = UserModel(
            name=register_data.user.name,
            email=register_data.user.email,
            password_hash=hash_password(register_data.user.password),
            role=register_data.user.role.strip(),
            organization_id=create_org.org_id
        )
        db.add(create_user)
        await db.flush()
        await db.commit()
        
        
        logger.info(
            f"""Registration successful for organization: {
                register_data.organization.name
            }, user: {
                register_data.user.email
            }"""
        )
        
        return RegisterResponse(
            organization=OrganizationResponse(
                org_id=create_org.org_id,
                name=create_org.name,
                type=create_org.type,
                email=create_org.email,
                phone=create_org.phone,
                address=create_org.address,
                created_at=create_org.created_at
            ),
            user=UserResponse(
                user_id=create_user.user_id,
                organization_id=create_user.organization_id,
                name=create_user.name,
                email=create_user.email,
                role=create_user.role,
                is_active=create_user.is_active,
                created_at=create_user.created_at
            ),
            
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    
    
@auth_router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login_user(
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_db)

) -> LoginResponse:
    
    try:
        logger.info(
            f"Login attempt for email: {login_data.email}"
        )
        email = select(
            UserModel
        ).where(
            UserModel.email == login_data.email
        )
        result = await db.execute(email)
        user = result.scalars().first()
        if not user:
            raise AuthenticationException(
                "Invalid email or password"
            )
        if not verify_password(login_data.password, user.password_hash):
            raise AuthenticationException(
                "Invalid email or password"
            )
        
        token = create_access_token(
            data={
                "user_id": str(user.user_id), 
                "email": user.email
            },
            expires_delta=timedelta(hours=1)
        )

        if not token:
            raise AuthenticationException(
                "Failed to create access token"
            )
        
        logger.info(
            f"Login successful for email: {login_data.email}"
        )
        return LoginResponse(
            access_token=token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    


@auth_router.get("/me-account", response_model=AccountMeResponse, status_code=status.HTTP_200_OK)
async def get_my_account(
        current_user: UserModel = Depends(get_current_user),
        current_org: OrganizationModel = Depends(get_current_organization)
) -> AccountMeResponse:
    try:
        return AccountMeResponse(
            user=UserResponse(
                user_id=current_user.user_id,
                organization_id=current_user.organization_id,
                name=current_user.name,
                email=current_user.email,
                role=current_user.role,
                is_active=current_user.is_active,
                created_at=current_user.created_at
            ),
            organization=OrganizationResponse(
                org_id=current_org.org_id,
                name=current_org.name,
                type=current_org.type,
                email=current_org.email,
                phone=current_org.phone,
                address=current_org.address,
                created_at=current_org.created_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    


@auth_router.put("/update-Account", response_model=AccountUpdateResponse, status_code=status.HTTP_200_OK)
async def update_my_account(
        update_data: AccountUpdateRequest,
        current_user: UserModel = Depends(get_current_user),
        current_org: OrganizationModel = Depends(get_current_organization),
        db: AsyncSession = Depends(get_db)
) -> AccountUpdateResponse:
    
    try:
        if update_data.user:
            # Email cannot be changed to a different value
            if update_data.user.email is not None and update_data.user.email != current_user.email:
                raise DatabaseException(
                    "User email cannot be changed"
                )
            if update_data.user.name is not None:
                current_user.name = update_data.user.name
            if update_data.user.role is not None:
                current_user.role = update_data.user.role
            if update_data.user.is_active is not None:
                current_user.is_active = update_data.user.is_active
        
        if update_data.organization:
            if update_data.organization.name is not None:
                current_org.name = update_data.organization.name
            if update_data.organization.type is not None:
                current_org.type = update_data.organization.type
            if update_data.organization.email is not None:
                current_org.email = update_data.organization.email
            if update_data.organization.phone is not None:
                current_org.phone = update_data.organization.phone
            if update_data.organization.address is not None:
                current_org.address = update_data.organization.address
        
        
        await db.flush()
        await db.commit()
        
        return AccountUpdateResponse(
            user=UserResponse(
                user_id=current_user.user_id,
                organization_id=current_user.organization_id,
                name=current_user.name,
                email=current_user.email,
                role=current_user.role,
                is_active=current_user.is_active,
                created_at=current_user.created_at
            ),
            organization=OrganizationResponse(
                org_id=current_org.org_id,
                name=current_org.name,
                type=current_org.type,
                email=current_org.email,
                phone=current_org.phone,
                address=current_org.address,
                created_at=current_org.created_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@auth_router.post("/forgot-password", response_model=ForgotPasswordResponse, status_code=status.HTTP_200_OK)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """
    Request password reset. Sends email with reset token.
    """
    try:
        logger.info(f"Password reset requested for email: {forgot_data.email}")
        
        # Find user by email
        stmt = select(UserModel).where(UserModel.email == forgot_data.email)
        result = await db.execute(stmt)
        user = result.scalars().first()

        # Don't reveal if email exists or not for security
        if not user:
            logger.warning(f"Password reset attempt for non-existent email: {forgot_data.email}")
            return ForgotPasswordResponse(
                message="If email exists, password reset link will be sent"
            )
        
        # Generate reset token
        reset_token = generate_password_reset_token()
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        # Store token in database
        db_token = PasswordResetToken(
            user_id=user.user_id,
            token=reset_token,
            expires_at=expires_at
        )
        db.add(db_token)
        await db.flush()
        await db.commit()
        
        # Send email with reset link
        try:
            send_password_reset_email(user.email, reset_token)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            # Don't fail the request, but log the error
        
        logger.info(f"Password reset token generated for user: {user.email}")
        
        return ForgotPasswordResponse(
            message="If email exists, password reset link will be sent"
        )
    except Exception as e:
        logger.error(f"Error in forgot_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@auth_router.post("/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
) -> PasswordResetResponse:
    """
    Reset password using token sent via email.
    Request body should include: email, token, new_password
    """
    try:
        logger.info(f"Password reset attempt for email: {reset_data.email}")
        
        # Find user by email
        stmt = select(UserModel).where(UserModel.email == reset_data.email)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise DatabaseException(
                "User with this email does not exist"
            )
        
        # Find and validate the reset token
        token_stmt = select(PasswordResetToken).where(
            (PasswordResetToken.user_id == user.user_id) &
            (PasswordResetToken.token == reset_data.token) &
            (PasswordResetToken.is_used == False)
        )
        token_result = await db.execute(token_stmt)
        reset_token = token_result.scalars().first()
        
        if not reset_token:
            logger.warning(f"Invalid or expired token for user: {user.email}")
            raise DatabaseException(
                "Invalid or expired reset token"
            )
        
        # Check if token has expired
        if reset_token.expires_at < datetime.utcnow():
            logger.warning(f"Expired token for user: {user.email}")
            raise DatabaseException(
                "Reset token has expired. Please request a new one."
            )
        
        # Update password
        user.password_hash = hash_password(reset_data.new_password)
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.used_at = datetime.utcnow()
        
        await db.flush()
        await db.commit()

        logger.info(f"Password reset successful for email: {reset_data.email}")

        return PasswordResetResponse(
            message="Password reset successfully"
        )
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
  