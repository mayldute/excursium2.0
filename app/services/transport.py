from typing import List

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, DeclarativeBase

from app.models import Transport, User, Carrier
from app.schemas import TransportCreate, TransportUpdate, TransportResponse
from app.utils import generate_presigned_url, upload_transport_photo_to_minio, delete_photo_from_minio
from app.core.constants import ALLOWED_IMAGE_TYPES

async def get_transport_and_validate_user(transport_id: int, current_user: User, db: AsyncSession) -> Transport:
    """Gets transport by ID and checks that the current user owns the associated carrier.

    Args:
        transport_id (int): ID of the transport to retrieve.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Transport: Transport instance if found and user is authorized.

    Raises:
        HTTPException: If transport does not exist (404) or user does not own the carrier (403).
    """
    # Get transport and associated carrier in one query
    result = await db.execute(
        select(Transport).options(selectinload(Transport.carrier)).where(Transport.id == transport_id)
    )
    transport = result.scalar_one_or_none()

    # Check existence of transport and ownership of carrier
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    if transport.carrier.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return transport


async def save_entity(entity: Transport, db: AsyncSession) -> None:
    """Saves a transport instance to the database and refreshes its state.

    Args:
        entity (Transport): Transport instance to save.
        db (AsyncSession): Asynchronous database session.
    """
    # Add entity to session, commit changes and refresh data
    db.add(entity)
    await db.commit()
    await db.refresh(entity)


async def create_transport_service(payload: TransportCreate, current_user: User, db: AsyncSession) -> TransportResponse:
    """Creates a new transport for the current user's carrier.

    Args:
        payload (TransportCreate): Pydantic model with data for creating transport.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        TransportResponse: Pydantic model with created transport data.

    Raises:
        HTTPException: If user does not own a carrier (403).
    """
    # Get carrier ID for current user
    result = await db.execute(select(Carrier.id).where(Carrier.user_id == current_user.id))
    carrier_id = result.scalar_one_or_none()

    # Ensure user has a registered carrier
    if not carrier_id:
        raise HTTPException(status_code=403, detail="Access denied: user does not own a carrier")

    # Create new transport instance from payload data
    transport = Transport(
        name=payload.name,
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        n_desk=payload.n_desk,
        n_seat=payload.n_seat,
        photo="transport_photos/default_bus.jpg",  # Set default photo
        luggage=payload.luggage,
        wifi=payload.wifi,
        tv=payload.tv,
        air_conditioning=payload.air_conditioning,
        toilet=payload.toilet,
        carrier_id=carrier_id
    )

    # Save transport to database
    await save_entity(transport, db)

    # Return transport as Pydantic model
    return TransportResponse.model_validate(transport)


async def update_transport_service(transport_id: int, payload: TransportUpdate, current_user: User, db: AsyncSession) -> TransportResponse:
    """Updates an existing transport by ID if user owns the carrier.

    Args:
        transport_id (int): ID of the transport to update.
        payload (TransportUpdate): Pydantic model with update data.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        TransportResponse: Pydantic model with updated transport data.

    Raises:
        HTTPException: If transport not found (404) or user does not own the carrier (403).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(transport_id, current_user, db)

    # Update fields from payload
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(transport, key, value)

    # Save updated transport
    await save_entity(transport, db)

    # Return updated transport as Pydantic model
    return TransportResponse.model_validate(transport)


async def get_transports_by_carrier_id_service(carrier_id: int, current_user: User, db: AsyncSession) -> List[TransportResponse]:
    """Gets a list of all transports for the specified carrier.

    Args:
        carrier_id (int): Carrier ID to get transports for.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        List[TransportResponse]: List of Pydantic models with transport data.

    Raises:
        HTTPException: If carrier not found (404), user does not own carrier (403), or no transports found (404).
    """
    # Get carrier with user data for ownership check
    result = await db.execute(
        select(Carrier).options(selectinload(Carrier.user)).where(Carrier.id == carrier_id)
    )
    carrier = result.scalar_one_or_none()

    # Check existence of carrier and ownership
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    if carrier.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get all transports for carrier
    result = await db.execute(select(Transport).where(Transport.carrier_id == carrier_id))
    transports = result.scalars().all()

    # Check if transports exist
    if not transports:
        raise HTTPException(status_code=404, detail="No transports found for this carrier")

    # Add presigned URLs for transport photos
    for transport in transports:
        transport.photo = generate_presigned_url(transport.photo)

    # Convert to Pydantic models
    return [TransportResponse.model_validate(transport) for transport in transports]


async def delete_transport_service(transport_id: int, current_user: User, db: AsyncSession) -> dict:
    """Deletes a transport by ID if user owns the carrier.

    Args:
        transport_id (int): ID of the transport to delete.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message about successful deletion and deleted transport ID.

    Raises:
        HTTPException: If transport not found (404) or user does not own the carrier (403).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(transport_id, current_user, db)

    # Delete transport from database
    await db.delete(transport)
    await db.commit()

    # Return success message
    return {'message': 'Transport successfully deleted', 'transport_id': transport_id}


async def upload_transport_photo_service(transport_id: int, file: UploadFile, current_user: User, db: AsyncSession) -> dict:
    """Uploads a transport photo to MinIO and updates the transport profile.

    Args:
        transport_id (int): ID of the transport to update photo for.
        file (UploadFile): Photo file to upload.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        dict: Dictionary with uploaded photo URL.

    Raises:
        HTTPException: If file not provided (400), file type not supported (400), transport not found (404), user does not own carrier (403), or upload failed (500).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(transport_id, current_user, db)

    # Check uploaded file
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: JPEG, PNG, WEBP."
        )

    # Upload new photo to MinIO
    photo_url = await upload_transport_photo_to_minio(file, transport.id)
    if not photo_url:
        raise HTTPException(status_code=500, detail="Failed to upload photo")

    # Delete previous photo if not default
    if transport.photo and transport.photo != "transport_photos/default_bus.jpg":
        delete_photo_from_minio(transport.photo)

    # Update transport photo URL
    transport.photo = photo_url
    await save_entity(transport, db)

    # Return new photo URL
    return {"photo_url": photo_url}