import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, RefreshToken
from app.core.config import settings

# JWT secret key for encoding and decoding tokens
SECRET_KEY = settings.jwt.jwt_secret_key

# Algorithm used for JWT encoding
ALGORITHM = settings.jwt.jwt_algorithm

# Expiration time for access tokens in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.jwt_access_token_expire_minutes

# Expiration time for refresh tokens in days
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt.jwt_refresh_token_expire_days

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token with the provided data and expiration time.

    Args:
        data (dict): The payload data to encode in the token (e.g., user ID and email).
        expires_delta (timedelta, optional): Custom expiration time. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: The encoded JWT access token.

    Raises:
        ValueError: If SECRET_KEY is not set.
        jwt.PyJWTError: If token encoding fails.
    """
    # Validate SECRET_KEY
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")

    # Prepare token payload
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})

    # Encode token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT refresh token with the provided data and expiration time.

    Args:
        data (dict): The payload data to encode in the token (e.g., user ID and email).
        expires_delta (timedelta, optional): Custom expiration time. Defaults to REFRESH_TOKEN_EXPIRE_DAYS.

    Returns:
        str: The encoded JWT refresh token.

    Raises:
        ValueError: If SECRET_KEY is not set.
        jwt.PyJWTError: If token encoding fails.
    """
    # Validate SECRET_KEY
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")

    # Prepare token payload
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})

    # Encode token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_tokens_for_user(user: User, db: AsyncSession) -> dict:
    """Generate access and refresh tokens for a user and store the refresh token in the database.

    Args:
        user (User): The user for whom to generate tokens.
        db (AsyncSession): The database session for saving the refresh token.

    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.

    Raises:
        ValueError: If SECRET_KEY is not set.
        jwt.PyJWTError: If token encoding fails.
    """
    # Prepare user data for token
    user_data = {
        "sub": str(user.id),
        "email": user.email,
    }

    # Generate access and refresh tokens
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    # Store refresh token in database
    new_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def create_activation_token(user_id: int) -> str:
    """Create a JWT activation token for a user, valid for 24 hours.

    Args:
        user_id (int): The ID of the user to associate with the token.

    Returns:
        str: The encoded JWT activation token.

    Raises:
        ValueError: If SECRET_KEY is not set.
        jwt.PyJWTError: If token encoding fails.
    """
    # Validate SECRET_KEY
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")

    # Prepare token payload
    payload = {
        "sub": str(user_id),
        "type": "activation",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    # Encode token
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_email_change_token(user_id: int, new_email: str) -> str:
    """Create a JWT email change token for a user, valid for 1 hour.

    Args:
        user_id (int): The ID of the user requesting the email change.
        new_email (str): The new email address to include in the token.

    Returns:
        str: The encoded JWT email change token.

    Raises:
        ValueError: If SECRET_KEY is not set or new_email is empty.
        jwt.PyJWTError: If token encoding fails.
    """
    # Validate inputs
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set")
    if not new_email:
        raise ValueError("New email cannot be empty")

    # Prepare token payload
    payload = {
        "sub": str(user_id),
        "new_email": new_email,
        "type": "email_change",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    # Encode token
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)