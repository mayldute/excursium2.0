import jwt
import os
from datetime import datetime, timedelta, timezone
from app.models import User, RefreshToken 
from sqlalchemy.ext.asyncio import AsyncSession

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_tokens_for_user(user: User, db: AsyncSession) -> dict:
    user_data = {
        "sub": str(user.id),
        "email": user.email,
    }

    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    new_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    db.add(new_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def create_activation_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "activation",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)