from fastapi import HTTPException, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, RefreshToken
from app.utils.security import verify_password
from app.utils.tokens import get_tokens_for_user
from app.utils.security import hash_password
from sqlalchemy import delete
from app.models.refresh_token import RefreshToken
from app.utils.tokens import SECRET_KEY, ALGORITHM, create_access_token
from jose import JWTError, jwt
from sqlalchemy.future import select
from datetime import datetime, timezone


async def authenticate_user(email: str, password: str, db: AsyncSession, request: Request):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return await get_tokens_for_user(user, db)

async def logout_user(refresh_token: str, db: AsyncSession):
    await db.execute(delete(RefreshToken).where(RefreshToken.token == refresh_token))
    await db.commit()

async def change_user_password(user: User, old_password: str, new_password:str, db:AsyncSession, request: Request):
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.hashed_password = hash_password(new_password)
    db.add(user)
    await db.commit()

async def refresh_user_token(refresh_token: str, db: AsyncSession):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    stored_token = result.scalar_one_or_none()

    if not stored_token or stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or not found")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = {"sub": str(user.id), "email": user.email}
    return {"access_token": create_access_token(user_data)}
    
