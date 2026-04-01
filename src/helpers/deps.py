from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.sessionmaker import async_session
from src.helpers.security import oauth2_scheme
from src.models.DatabaseModels import UserModel, OrganizationModel
from fastapi import Depends
from src.exceptions.custom_exception import DatabaseException
from src.exceptions.custom_exception import AuthenticationException
from src.helpers.security import decode_access_token



async def get_db():
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()   


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> UserModel:
    
    try:
        payload = decode_access_token(token)
        email: str = payload.get("email")
        if email is None:
            raise AuthenticationException(
                "Invalid authentication credentials"
            )
    except JWTError:
        raise AuthenticationException(
            "Invalid authentication credentials"
        )
    
    stmt = select(UserModel).where(UserModel.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user is None:
        raise AuthenticationException(
            "Invalid authentication credentials"
        )
    return user


async def get_current_organization(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> OrganizationModel:
    
    stmt = select(
        OrganizationModel
    ).where(
        OrganizationModel.org_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    organization = result.scalars().first()
    
    if organization is None:
        raise AuthenticationException(
            "Organization not found"
        )
    return organization

