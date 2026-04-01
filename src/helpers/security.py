import passlib
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from src.config.config import settings
from src.exceptions.custom_exception import AuthenticationException
import secrets


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(
            plain_password, hashed_password
        )
    except UnknownHashError:
        raise AuthenticationException("Invalid password hash")
    
    
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:

    try:
        to_encode = data.copy()
        expires = datetime.utcnow() + (expires_delta or timedelta(minutes=50))
        to_encode.update({"exp": expires})
        encode_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encode_jwt
    except Exception as e:
        raise AuthenticationException(
            "Error creating access token"
        ) from e  
    

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise AuthenticationException(
            "Invalid access token"
        ) from e


def generate_password_reset_token() -> str:
    """
    Generate a secure random token for password reset
    """
    return secrets.token_urlsafe(32)