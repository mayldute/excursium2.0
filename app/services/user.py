from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.utils.security import verify_password
from app.utils.tokens import get_tokens_for_user
from app.utils.security import hash_password

async def authenticate_user(email: str, password: str, db: AsyncSession, request: Request):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return get_tokens_for_user(user)

async def change_user_password(user: User, old_password: str, new_password:str, db:AsyncSession, request: Request):
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.hashed_password = hash_password(new_password)
    db.add(user)
    await db.commit()
