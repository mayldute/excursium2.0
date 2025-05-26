import httpx
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4

from app.models import User, Client, OAuthState
from app.schemas import ClientCreate, ClientUpdate, CompleteRegistration
from app.utils import( 
    hash_password, 
    create_activation_token, 
    send_email, 
    create_access_token, 
    generate_presigned_url
)

from app.core.config import settings
from app.core.oauth import oauth

# Define a mapping for email fields based on the OAuth provider
EMAIL_FIELDS = {
    "google": "email",
    "yandex": "default_email"
}

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
    photo_url = generate_presigned_url(client.user.photo)
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


async def initiate_oauth_login(provider_name: str, db: AsyncSession) -> dict:
    """Initiate OAuth login by generating an authorization URL for the specified provider.

    Args:
        provider_name (str): The OAuth provider name (e.g., 'google', 'yandex').
        db (AsyncSession): The database session for saving the OAuth state.

    Returns:
        dict: A dictionary containing the authorization URL and state.

    Raises:
        HTTPException: If the provider is invalid or the authorization URL cannot be generated.
    """
    if provider_name not in ["google", "yandex"]:
        raise HTTPException(status_code=400, detail="Invalid OAuth provider")

    # Set redirect URI based on provider
    redirect_uri = (
        settings.google.google_redirect_uri if provider_name == "google"
        else settings.yandex.yandex_redirect_uri
    )
    # Define OAuth scope for user data access
    scope = "openid email profile" if provider_name == "google" else "login:email"

    try:
        # Generate authorization URL with unique state
        auth_url = await oauth.create_client(provider_name).create_authorization_url(
            redirect_uri,
            state=str(uuid4()),
            scope=scope
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate authorization URL: {str(e)}")

    # Store state in database with 10-minute expiry
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    state_record = OAuthState(
        state=auth_url['state'],
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc)
    )
    db.add(state_record)
    await db.commit()

    return {"url": auth_url['url'], "state": auth_url['state']}

async def handle_oauth_callback(provider_name: str, request: Request, state: str, db: AsyncSession) -> dict:
    """Handle the callback from an OAuth provider after user authorization.

    Args:
        provider_name (str): The OAuth provider name (e.g., 'google', 'yandex').
        request (Request): The incoming request containing query parameters (e.g., authorization code).
        state (str): The state parameter to verify the request.
        db (AsyncSession): The database session for querying and saving data.

    Returns:
        dict: For existing users, returns {"access_token": str}. For new users, returns {"access_token": str, "requires_completion": bool}.

    Raises:
        HTTPException: If the authorization code is missing, the state is invalid/expired, token exchange fails, or the account has no email.
    """
    if provider_name not in ["google", "yandex"]:
        raise HTTPException(status_code=400, detail="Invalid OAuth provider")

    # Extract authorization code from request
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    # Verify the state parameter
    state_record = await db.execute(select(OAuthState).where(OAuthState.state == state))
    state_record = state_record.scalar_one_or_none()
    if not state_record or state_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    await db.delete(state_record)
    await db.commit()

    # Configure token exchange parameters
    token_params = {
        "code": code,
        "client_id": settings.google.google_client_id if provider_name == "google" else settings.yandex.yandex_client_id,
        "client_secret": settings.google.google_client_secret if provider_name == "google" else settings.yandex.yandex_client_secret,
        "redirect_uri": settings.google.google_redirect_uri if provider_name == "google" else settings.yandex.yandex_redirect_uri,
        "grant_type": "authorization_code",
    }

    # Set provider-specific token endpoint
    token_url = (
        "https://accounts.google.com/o/oauth2/token" if provider_name == "google"
        else "https://oauth.yandex.ru/token"
    )

    # Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, data=token_params)
            response.raise_for_status()
            token_data = response.json()
            if "error" in token_data:
                raise HTTPException(status_code=400, detail=token_data.get("error_description", "Failed to obtain access token"))
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")

    # Fetch user information using the access token
    try:
        user_info = await oauth.create_client(provider_name).userinfo(token=token_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch user info: {str(e)}")

    # Extract email from provider-specific field
    email_field = EMAIL_FIELDS.get(provider_name)
    email = user_info.get(email_field)
    if not email:
        raise HTTPException(status_code=400, detail=f"{provider_name.capitalize()} account has no email")

    # Check if the user already exists
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()

    if user:
        if not user.is_oauth_user:
            raise HTTPException(status_code=400, detail="This email is registered locally. Please login with email and password.")
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token}
    else:
        new_user = User(email=email, is_active=False, is_oauth_user=True, photo="user_photos/standard-photo.jpg")
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        new_client = Client(user_id=new_user.id, client_type="IND")
        db.add(new_client)
        await db.commit()

        token = create_access_token({"sub": str(new_user.id)})
        return {"access_token": token, "requires_completion": True}

async def complete_social_registration(payload: CompleteRegistration, current_user: User, db: AsyncSession) -> dict:
    """Complete the registration process for a user who logged in via social OAuth.

    Args:
        payload (CompleteRegistration): The data to update user fields (e.g., name, phone).
        current_user (User): The authenticated user completing the registration.
        db (AsyncSession): The database session for querying and saving data.

    Returns:
        dict: A dictionary with a success message, e.g., {"detail": "Registration completed"}.

    Raises:
        HTTPException: If the user is already active, the client is not found, or the client type is not 'IND'.
    """
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="User already activated")

    # Verify client exists and is of type 'IND'
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()

    if not client or client.client_type != "IND":
        raise HTTPException(status_code=400, detail="Only IND clients can complete this step")

    # Update user fields with provided data
    user_data = payload
    if user_data:
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(current_user, field, value)

    # Activate user account
    current_user.is_active = True
    await db.commit()

    return {"detail": "Registration completed"}