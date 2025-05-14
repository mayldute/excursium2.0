from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserLogin, Token, PasswordChangeRequest
from app.dependencies.get_db import get_db
from app.services.user import activate_user_by_token, authenticate_user, logout_user, change_user_password, refresh_user_token
from app.models import User
from app.dependencies.user import get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["[auth] user"])
oauth2_scheme = HTTPBearer()

@router.get("/activate", summary="Activate user account via link")
async def activate_user(token: str, db: AsyncSession = Depends(get_db)):
    return await activate_user_by_token(token, db)

@router.post("/login", summary="User login", response_model=Token)
async def login(
    payload: UserLogin, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await authenticate_user(payload.email, payload.password, db, request)

@router.post("/logout", summary="Logout and revoke refresh token")
async def logout(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await logout_user(token.credentials, db)

@router.post("/change-password", summary="Change password")
async def change_password(
    payload: PasswordChangeRequest, 
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await change_user_password(current_user, payload.old_password, payload.new_password, db, request)

@router.post("/refresh", summary="Get new access token using refresh token")
async def refresh_access_token(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await refresh_user_token(token.credentials, db)

