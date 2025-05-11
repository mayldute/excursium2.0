from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserLogin, Token, PasswordChangeRequest
from app.dependencies.get_db import get_db
from app.services.user import authenticate_user
from app.services.user import change_user_password
from app.models import User
from app.dependencies.user import get_current_user

router = APIRouter(prefix="/auth", tags=["[auth] user"])

@router.post("/login", summary="User login", response_model=Token)
async def login(
    payload: UserLogin, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await authenticate_user(payload.email, payload.password, db, request)

@router.post("/change-password", summary="Change password")
async def change_password(
    payload: PasswordChangeRequest, 
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await change_user_password(current_user, payload.old_password, payload.new_password, db, request)