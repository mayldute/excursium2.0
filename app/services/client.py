from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User, Client
from app.schemas import ClientCreate, ClientUpdate
from app.utils import hash_password, create_activation_token, send_email
from app.core.config import settings

async def get_owned_client_or_403(client_id: int, current_user: User, db: AsyncSession) -> Client:
    """Fetch a client by ID and verify user ownership.

    Args:
        client_id (int): The ID of the client to fetch.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying.

    Returns:
        Client: The client object if found and owned by the user.

    Raises:
        HTTPException: If the client is not found or the user does not have ownership (status code 403).
    """
    client = await db.get(Client, client_id)

    if not client or client.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return client


async def register_client_service(payload: ClientCreate, db: AsyncSession) -> dict:
    """Register a new client and associated user, sending an activation email.

    Args:
        payload (ClientCreate): Data for creating the client and user.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary containing a success message and, in debug mode, the activation link.

    Raises:
        HTTPException: If a user with the provided email already exists (status code 409).
    """
    user_data = payload.user

    # Check for existing user with the same email
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=409, detail="A user with this email already exists")

    # Create and save the new user
    new_user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        hashed_password=hash_password(user_data.password1),
        photo="user_photos/standard-photo.jpg",
    )

    db.add(new_user)
    await db.flush() 

    # Create and save the client
    client_kwargs = {
        "user_id": new_user.id,
        "client_type": payload.client_type,
        "legal_type": payload.legal_type,
        "custom_type": payload.custom_type,
        "company_name": payload.company_name,
        "inn": payload.inn,
        "kpp": payload.kpp,
    }

    client = Client(**client_kwargs)
    db.add(client)
    await db.commit()

    # Generate and send activation email
    activation_token = create_activation_token(new_user.id)
    activation_link = f"https://your-frontend.com/activate?token={activation_token}"

    await send_email(
        to=new_user.email,
        subject="Activate your account",
        body=f"Click to activate: {activation_link}"
    )

    return {
        "message": "Registration successful. Please check your email to activate your account.",
        "activation_link": activation_link if settings.app.debug else None,
    }


async def get_client_service(client_id: int, current_user: User, db: AsyncSession) -> Client:
    """Retrieve a client by ID, including the user's photo URL.

    Args:
        client_id (int): The ID of the client to retrieve.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying.

    Returns:
        Client: The client object with the user's photo URL.

    Raises:
        HTTPException: If the client is not found, user lacks ownership (403), or user is not active (403).
    """
    client = await get_owned_client_or_403(client_id, current_user, db)
    
    if not client.user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")
    
    # Update user photo with a presigned URL
    photo_url = await client.user.get_photo_url()
    client.user.photo = photo_url

    return client


async def update_client_service(client_id: int, payload: ClientUpdate, current_user: User, db: AsyncSession) -> Client:
    """Update client and associated user information.

    Args:
        client_id (int): The ID of the client to update.
        payload (ClientUpdate): The data to update the client and user.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        Client: The updated client object.

    Raises:
        HTTPException: If the client is not found, user lacks ownership (403), or user is not active (403).
    """
    client = await get_owned_client_or_403(client_id, current_user, db)
    
    if not client.user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    # Update user attributes if provided
    data = payload.model_dump(exclude_unset=True)
    user_data = data.pop("user", None)

    if user_data:
        for key, value in user_data.items():
            setattr(client.user, key, value)

    # Update client attributes
    for key, value in data.items():
        setattr(client, key, value)

    db.add(client)
    await db.commit()

    return client

async def delete_client_service(client_id: int, current_user: User, db:AsyncSession) -> dict:
    """"Soft delete a client by deactivating the user and setting the deletion timestamp.

    Args:
        client_id (int): The ID of the client to delete.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a confirmation message.

    Raises:
        HTTPException: If the client is not found or user lacks ownership (403).
    """
    client = await get_owned_client_or_403(client_id, current_user, db)
    
    # Deactivate user and mark deletion time
    client.user.is_active = False
    client.user.deleted_at = datetime.now(timezone.utc)
    
    await db.flush()
    await db.commit()

    return {"detail": "Deleted"}

