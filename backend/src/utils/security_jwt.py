import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from typing import Optional

from config import settings
from src.utils.postegre_connexion import get_async_sqldb
from src.schemas.users import TokenData, UserOut

# Configuration
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt.

    Args:
        password: The plain-text password to hash.

    Returns:
        The bcrypt-hashed password string.
    """
    # bcrypt attend des bytes
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a bcrypt hash.

    Args:
        plain_password: The plain-text password to verify.
        hashed_password: The bcrypt hash to verify against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    """Generates a JSON Web Token (JWT) access token.

    Args:
        data: The claims dictionary to encode in the token.

    Returns:
        The encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from sqlmodel import select
from src.models.users import Utilisateur

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_sqldb)
) -> Utilisateur:
    """Retrieves the currently authenticated user from the JWT token.

    Args:
        token: The raw JWT bearer token.
        session: The active database session.

    Returns:
        The authenticated Utilisateur instance.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception

    statement = select(Utilisateur).where(Utilisateur.email == token_data.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user