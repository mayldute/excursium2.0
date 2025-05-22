from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from pydantic import EmailStr

from fastapi import HTTPException, UploadFile
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import (
    User, 
    RefreshToken, 
    ChangeEmail, 
    RefreshToken
)

from app.utils import (
    verify_password, 
    hash_password, 
    send_email, 
    upload_photo_to_minio, 
    delete_photo_from_minio,
    SECRET_KEY, 
    ALGORITHM, 
    create_access_token, 
    get_tokens_for_user, 
    create_email_change_token
)


from app.core.config import settings

# Allowed MIME types for user photo uploads
ALLOWED_IMAGE_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

async def save_user(user: User, db: AsyncSession) -> None:
    """Save a user to the database.

    Args:
        user (User): The user object to save.
        db (AsyncSession): The database session for saving.

    Returns:
        None
    """
    db.add(user)
    await db.commit()


async def authenticate_user(email: str, password: str, db: AsyncSession) -> dict:
    """Authenticate a user by email and password, returning access and refresh tokens.

    Args:
        email (str): The user's email address.
        password (str): The user's password.
        db (AsyncSession): The database session for querying.

    Returns:
        dict: A dictionary containing access and refresh tokens.

    Raises:
        HTTPException: If credentials are invalid (401), or the user is not active (403).
    """
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(403, "Please activate your account")
    
    # Generate and return tokens
    return await get_tokens_for_user(user, db)


async def logout_user(refresh_token: str, db: AsyncSession) -> dict:
    """Log out a user by removing their refresh token from the database.

    Args:
        refresh_token (str): The refresh token to remove.
        db (AsyncSession): The database session for querying and deleting.

    Returns:
        dict: A dictionary with a success message.
    """
    # Remove refresh token
    await db.execute(delete(RefreshToken).where(RefreshToken.token == refresh_token))
    await db.commit() 

    return {"message": "Logout successful"}


async def change_user_password(user: User, old_password: str, new_password:str, db:AsyncSession) -> dict:
    """Change a user's password after verifying the old password.

    Args:
        user (User): The authenticated user.
        old_password (str): The current password to verify.
        new_password (str): The new password to set.
        db (AsyncSession): The database session for saving.

    Returns:
        dict: A dictionary with a success message.

    Raises:
        HTTPException: If the old password is invalid (401).
    """
    # Verify old password
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update password and save
    user.hashed_password = hash_password(new_password)
    await save_user(user, db=db)

    return {"message": "Password changed successfully"}


async def refresh_user_token(refresh_token: str, db: AsyncSession) -> dict:
    """Refresh an access token using a valid refresh token.

    Args:
        refresh_token (str): The refresh token to validate.
        db (AsyncSession): The database session for querying.

    Returns:
        dict: A dictionary containing a new access token.

    Raises:
        HTTPException: If the token is invalid (401), expired (401), or the user is not found (404).
    """
    # Decode and validate refresh token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Verify stored token
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    stored_token = result.scalar_one_or_none()

    if not stored_token or stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or not found")

    # Fetch user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate new access token
    user_data = {"sub": str(user.id), "email": user.email}

    return {"access_token": create_access_token(user_data)}
    

async def activate_user_by_token(token: str, db: AsyncSession) -> dict:
    """Activate a user account using a valid activation token.

    Args:
        token (str): The activation token to validate.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a success message.

    Raises:
        HTTPException: If the token is invalid (400), expired (400), or the user is not found (404).
    """
    # Decode and validate activation token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "activation":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Fetch user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_active:
        return {"message": "Account already activated"}

    # Activate user and save
    user.is_active = True
    await save_user(user, db=db)

    return {"message": "Account successfully activated"}


async def restore_user_service(user_email: str, db: AsyncSession) -> dict:
    """Restore a deleted user account if within the 30-day recovery period.

    Args:
        user_email (str): The email of the user to restore.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a success message.

    Raises:
        HTTPException: If the user is not found (404), already active (400), or recovery period has expired (403).
    """
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=400, detail="User is already active")

    # Check recovery period
    if not user.deleted_at or user.deleted_at < datetime.now(timezone.utc) - timedelta(days=30):
        raise HTTPException(status_code=403, detail="Recovery period has expired")

    # Restore user
    user.is_active = True
    user.deleted_at = None

    await save_user(user, db=db)

    return {"status": "restored"}

async def change_user_email_service(user: User, new_email: EmailStr, db: AsyncSession) -> dict:
    """Initiate an email change and send a confirmation link to the new email.

    Args:
        user (User): The authenticated user requesting the email change.
        new_email (EmailStr): The new email address to set.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a success message and, in debug mode, the activation link.

    Raises:
        HTTPException: If the new email is already in use (400).
    """
    # Check if new email is already in use
    result = await db.execute(select(User).where(User.email == new_email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")
    
    # Clear previous email change requests
    await db.execute(delete(ChangeEmail).where(ChangeEmail.user_id == user.id))

    # Create email change token and record
    email_change_token = create_email_change_token(user.id, str(new_email))
    email_change_link = f"https://your-frontend.com/activate?token={email_change_token}"

    change_email = ChangeEmail(
        user_id=user.id,
        new_email=new_email,
        token=email_change_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    db.add(change_email)
    await db.commit()

    # Send confirmation email
    await send_email(
        to=change_email.new_email,
        subject="Confirm your new email address",
        body=f"To confirm your new email, click the link: {email_change_link}"
    )

    return {
        "message": "Change email adress successful. Please check your email to confirm your new email.",
        "activation_link": email_change_link if settings.DEBUG else None,
    }

async def confirm_email_change(token: str, db: AsyncSession) -> dict:
    """Confirm an email change using a valid token.

    Args:
        token (str): The email change token to validate.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a success message.

    Raises:
        HTTPException: If the token is invalid (404), expired (403), or email mismatch occurs (400).
    """
    # Fetch email change record
    result = await db.execute(select(ChangeEmail).where(ChangeEmail.token == token))
    change = result.scalar_one_or_none()

    if not change:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    if change.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Token expired")

    # Validate token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_email = payload.get("new_email")

    if token_email != change.new_email:
        raise HTTPException(status_code=400, detail="Token email mismatch")

    # Update user email
    user = await db.get(User, change.user_id)
    user.email = change.new_email

    # Remove email change record
    await db.delete(change)
    await db.flush()
    await db.commit()

    return {"detail": "Email successfully updated"}

async def upload_photo_service(user: User, file: UploadFile, db: AsyncSession) -> dict:
    """Upload a user's photo to MinIO and update their profile.

    Args:
        user (User): The authenticated user.
        file (UploadFile): The photo file to upload.
        db (AsyncSession): The database session for saving.

    Returns:
        dict: A dictionary containing the URL of the uploaded photo.

    Raises:
        HTTPException: If no file is provided (400), file type is unsupported (400), or upload fails (500).
    """
    # Validate file
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: JPEG, PNG, WEBP."
        )
    
    # Upload photo to MinIO
    photo_url = await upload_photo_to_minio(file, user.id)

    if not photo_url:
        raise HTTPException(status_code=500, detail="Failed to upload photo")
    
    # Delete previous photo if not default
    if user.photo and user.photo != "user_photos/standard-photo.jpg":
        delete_photo_from_minio(user.photo)

    # Update user photo
    user.photo = photo_url
    await save_user(user, db=db)

    return {"photo_url": photo_url}