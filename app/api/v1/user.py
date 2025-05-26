from pydantic import EmailStr

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    UserLogin, 
    Token, 
    PasswordChangeRequest,
    EmailRequest
)

from app.dependencies.get_db import get_db
from app.dependencies.context import get_common_context, CommonContext
from app.services.user import (
    activate_user_by_token, 
    authenticate_user, 
    logout_user, 
    change_user_password, 
    refresh_user_token, 
    restore_user_service,
    change_user_email_service, 
    confirm_email_change, 
    upload_photo_service
)

# Initialize API router for user routes
router = APIRouter(prefix="/auth", tags=["[auth] user"])
# Initialize HTTPBearer for token authentication
oauth2_scheme = HTTPBearer()

@router.get("/activate", summary="Activate user account via link", status_code=200)
async def activate_user(
    token: str, 
    db: AsyncSession = Depends(get_db)
):
    # Activate user account using token
    return await activate_user_by_token(token, db)


@router.post("/login", summary="User login", response_model=Token, status_code=200)
async def login(
    payload: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    # Authenticate user and return access and refresh tokens
    return await authenticate_user(payload.email, payload.password, db)


@router.post("/logout", summary="Logout and revoke refresh token", status_code=204)
async def logout(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
): 
    # Logout user and revoke refresh token
    return await logout_user(token.credentials, db)


@router.post("/change-password", summary="Change password", status_code=200)
async def change_password(
    payload: PasswordChangeRequest, 
    context: CommonContext = Depends(get_common_context)
):
    # Change user password
    return await change_user_password(
        context.current_user, 
        payload.old_password, 
        payload.new_password, 
        context.db
    )


@router.post("/refresh", summary="Get new access token using refresh token", status_code=200)
async def refresh_access_token(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Refresh access token using refresh token
    return await refresh_user_token(token.credentials, db)


@router.patch("/restore", summary="Restore user by email", status_code=200)
async def restore_client(
    payload: EmailRequest,
    db: AsyncSession = Depends(get_db)
):
    # Restore user account using email
    return await restore_user_service(payload.email, db)


@router.post("/change-email", summary="Change email", status_code=200)
async def change_email(
    new_email: EmailStr,
    context: CommonContext = Depends(get_common_context)
):
    # Change user email
    return await change_user_email_service(context.current_user, new_email, context.db)


@router.get("/activate-email", summary="Activate email change")
async def activate_email_change(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    # Activate email change using token
    return await confirm_email_change(token, db)


@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    context: CommonContext = Depends(get_common_context)
):
    # Upload user photo
    return await upload_photo_service(context.current_user, file, context.db)