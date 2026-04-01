from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from src.helpers.deps import get_current_user, get_current_organization
from src.helpers.security import hash_password, verify_password, create_access_token
from src.schema.Schemas import LoginResponse, RegisterRequest, RegisterResponse, LoginRequest, OrganizationResponse, UserResponse, AccountMeResponse
from src.helpers.deps import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.DatabaseModels import UserModel, OrganizationModel
from src.exceptions.custom_exception import DatabaseException, AuthenticationException
from datetime import timedelta
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
