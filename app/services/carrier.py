from typing import List
from asyncio import gather, to_thread
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import (
    User, 
    Carrier, 
    Docs, 
    DocTypeEnum
)

from app.schemas import (
    CarrierCreate, 
    CarrierUpdate, 
    CarrierResponse,
    CarrierDocsResponse,
)

from app.utils import (
    hash_password, 
    create_activation_token, 
    send_email, 
    upload_docs_to_minio, 
    generate_presigned_url
)

from app.core.config import settings
from app.core.constants import ALLOWED_DOC_TYPES

async def get_owned_carrier_or_403(carrier_id: int, current_user: User, db: AsyncSession) -> Carrier:
    """Fetch a carrier by ID and verify user ownership.

    Args:
        carrier_id (int): The ID of the carrier to fetch.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying.

    Returns:
        Carrier: The carrier object if found and owned by the user.

    Raises:
        HTTPException: If the carrier is not found or the user does not have ownership (status code 403).
    """
    carrier = await db.get(Carrier, carrier_id)

    if not carrier or carrier.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return carrier


async def register_carrier_service(payload: CarrierCreate, db: AsyncSession) -> dict:
    """Register a new carrier and associated user, sending an activation email.

    Args:
        payload (CarrierCreate): Data for creating the carrier and user.
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

    # Create and save the carrier
    carrier_kwargs = {
        "user_id": new_user.id,
        "legal_type": payload.legal_type,
        "custom_type": payload.custom_type,
        "company_name": payload.company_name,
        "inn": payload.inn,
        "kpp": payload.kpp,
    }

    carrier = Carrier(**carrier_kwargs)
    db.add(carrier)
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
        "activation_link": activation_link if settings.app.debug else None
    }


async def get_carrier_service(carrier_id: int, current_user: User, db: AsyncSession) -> CarrierResponse:
    """Retrieve a carrier by ID, including the user's photo URL.

    Args:
        carrier_id (int): The ID of the carrier to retrieve.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying.

    Returns:
        Carrier: The carrier object with the user's photo URL.

    Raises:
        HTTPException: If the carrier is not found, user lacks ownership (403), or user is not active (403).
    """
    carrier = await get_owned_carrier_or_403(carrier_id, current_user, db)

    if not carrier.user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")
    
    # Update user photo with a presigned URL
    photo_url = generate_presigned_url(carrier.user.photo)
    carrier.user.photo = photo_url

    return CarrierResponse.model_validate(carrier)


async def update_carrier_service(carrier_id: int, payload: CarrierUpdate, current_user: User, db: AsyncSession) -> CarrierResponse:
    """Update carrier and associated user information.

    Args:
        carrier_id (int): The ID of the carrier to update.
        payload (CarrierUpdate): The data to update the carrier and user.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        Carrier: The updated carrier object.

    Raises:
        HTTPException: If the carrier is not found, user lacks ownership (403), or user is not active (403).
    """
    carrier = await get_owned_carrier_or_403(carrier_id, current_user, db)
    
    if not carrier.user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    # Update user attributes if provided
    data = payload.model_dump(exclude_unset=True)
    user_data = data.pop("user", None)

    if user_data:
        for key, value in user_data.items():
            setattr(carrier.user, key, value)

    # Update carrier attributes
    for key, value in data.items():
        setattr(carrier, key, value)

    db.add(carrier)
    await db.commit()

    return CarrierResponse.model_validate(carrier)


async def delete_carrier_service(carrier_id: int, current_user: User, db:AsyncSession) -> dict:
    """Soft delete a carrier by deactivating the user and setting the deletion timestamp.

    Args:
        carrier_id (int): The ID of the carrier to delete.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a confirmation message.

    Raises:
        HTTPException: If the carrier is not found or user lacks ownership (403).
    """
    carrier = await get_owned_carrier_or_403(carrier_id, current_user, db)
    
    # Deactivate user and mark deletion time
    carrier.user.is_active = False
    carrier.user.deleted_at = datetime.now(timezone.utc)

    await db.flush()
    await db.commit()

    return {"detail": "Deleted"}


async def upload_carrier_docs_service(carrier_id: int, files: List[UploadFile], doc_type: DocTypeEnum, current_user: User, db: AsyncSession) -> dict:
    """Upload documents for a carrier, validate file types, and return document IDs.

    Args:
        carrier_id (int): The ID of the carrier to associate documents with.
        files (List[UploadFile]): List of files to upload.
        doc_type (DocTypeEnum): The type of documents being uploaded.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying and saving.

    Returns:
        dict: A dictionary with a success message, count of uploaded documents, and their IDs.

    Raises:
        HTTPException: If no files are provided (400), file type is unsupported (400), upload fails (500), or user lacks ownership (403).
    """
    carrier = await get_owned_carrier_or_403(carrier_id, current_user, db)

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    uploaded_docs = []

    for file in files:
        # Validate file types
        if file.content_type not in ALLOWED_DOC_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_DOC_TYPES)}"
            )

        # Upload file to MinIO
        file_path = await upload_docs_to_minio(file, carrier.id)

        if not file_path:
            raise HTTPException(status_code=500, detail="Failed to upload one of the documents")

        # Save document record to database
        doc = Docs(
            doc_type=doc_type,
            file_path=file_path,
            carrier_id=carrier.id
        )

        db.add(doc)
        uploaded_docs.append(doc)

    await db.commit()
    # Refresh only the last document to ensure its state is up-to-date
    await db.refresh(uploaded_docs[-1]) 

    return {
        "detail": "Documents uploaded successfully",
        "uploaded_count": len(uploaded_docs),
        "doc_ids": [doc.id for doc in uploaded_docs]
    }


async def get_carrier_docs_service(carrier_id: int, current_user: User, db: AsyncSession) -> List[CarrierDocsResponse]:
    """Retrieve all documents for a carrier with presigned URLs.

    Args:
        carrier_id (int): The ID of the carrier whose documents are retrieved.
        db (AsyncSession): The database session for querying.
        current_user (User): The authenticated user making the request.

    Returns:
        List[CarrierDocsResponse]: A list of documents with presigned URLs.

    Raises:
        HTTPException: If no documents are found (404) or user lacks ownership (403).
    """
    result = await db.execute(select(Docs).where(Docs.carrier_id == carrier_id))
    docs = result.scalars().all()

    await get_owned_carrier_or_403(carrier_id, current_user, db)

    if not docs:
        raise HTTPException(status_code=404, detail="No documents found for this carrier")
    
    # Generate presigned URLs for all documents concurrently
    docs_urls = await gather(*[to_thread(generate_presigned_url, doc.file_path) for doc in docs])

    for doc, doc_url in zip(docs, docs_urls):
        doc.file_path = doc_url

    return [CarrierDocsResponse.model_validate(doc) for doc in docs]