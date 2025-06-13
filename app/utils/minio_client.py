import io
import logging
from uuid import uuid4
from datetime import timedelta

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile

from app.core.config import settings

# Logger for MinIO-related operations
logger = logging.getLogger(__name__)

# MinIO client for interacting with the storage service
minio_client = Minio(
    settings.minio.minio_endpoint,
    access_key=settings.minio.minio_access_key,
    secret_key=settings.minio.minio_secret_key,
    secure=settings.minio.minio_secure
)


async def upload_file_to_minio(file: UploadFile, object_name: str) -> str:
    """Upload a file to MinIO and return the object name.

    Args:
        file (UploadFile): The file to upload.
        object_name (str): The name to assign to the object in MinIO.

    Returns:
        str: The object name in MinIO.

    Raises:
        S3Error: If the upload to MinIO fails due to server issues or
            invalid configuration.
    """
    # Read file content
    content = await file.read()

    # Upload file to MinIO
    minio_client.put_object(
        bucket_name=settings.minio.minio_bucket_name,
        object_name=object_name,
        data=io.BytesIO(content),
        length=len(content),
        content_type=file.content_type
    )

    return object_name


async def upload_photo_to_minio(file: UploadFile, user_id: int) -> str:
    """Upload a user photo to MinIO and return the generated object name.

    Args:
        file (UploadFile): The photo file to upload.
        user_id (int): The ID of the user associated with the photo.

    Returns:
        str: The object name in MinIO
            (e.g., 'user_photos/<user_id>_<uuid>.<ext>').

    Raises:
        S3Error: If the upload to MinIO fails due to server issues or
            invalid configuration.
        ValueError: If the file has no extension.
    """
    # Generate object name with user ID and UUID
    file_ext = file.filename.split(".")[-1]
    if not file_ext:
        raise ValueError("File has no extension")
    object_name = f"user_photos/{user_id}_{uuid4().hex}.{file_ext}"

    # Upload file to MinIO
    return await upload_file_to_minio(file, object_name)


async def upload_docs_to_minio(file: UploadFile, carrier_id: int) -> str:
    """Upload a document to MinIO and return the generated object name.

    Args:
        file (UploadFile): The document file to upload.
        carrier_id (int): The ID of the carrier associated with the document.

    Returns:
        str: The object name in MinIO
            (e.g., 'carrier_docs/<carrier_id>_<uuid>.<ext>').

    Raises:
        S3Error: If the upload to MinIO fails due to server issues or
            invalid configuration.
        ValueError: If the file has no extension.
    """
    # Generate object name with carrier ID and UUID
    file_ext = file.filename.split(".")[-1]
    if not file_ext:
        raise ValueError("File has no extension")
    object_name = f"carrier_docs/{carrier_id}_{uuid4().hex}.{file_ext}"

    # Upload file to MinIO
    return await upload_file_to_minio(file, object_name)


def generate_presigned_url(object_name: str) -> str:
    """Generate a presigned URL for accessing an object in MinIO,
        valid for 10 minutes.

    Args:
        object_name (str): The name of the object in MinIO.

    Returns:
        str: The presigned URL for accessing the object.

    Raises:
        S3Error: If the URL generation fails due to server issues or
            invalid object name.
    """
    # Generate presigned URL
    try:
        url = minio_client.presigned_get_object(
            settings.minio.minio_bucket_name,
            object_name,
            expires=timedelta(minutes=10)
        )
    except S3Error as e:
        logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
        raise

    return url


def delete_photo_from_minio(object_name: str) -> None:
    """Delete an object from MinIO, logging any errors without raising them.

    Args:
        object_name (str): The name of the object to delete.

    Returns:
        None
    """
    # Attempt to delete object from MinIO
    try:
        minio_client.remove_object(
            bucket_name=settings.minio_bucket_name,
            object_name=object_name
        )
    except Exception as e:
        logger.warning(f"Error deleting photo from MinIO: {e}")


async def upload_transport_photo_to_minio(
    file: UploadFile,
    transport_id: int
) -> str:
    """Upload a transport photo to MinIO and return the generated object name.

    Args:
        file (UploadFile): The photo file to upload.
        transport_id (int): The ID of the transport associated with the photo.

    Returns:
        str: The object name in MinIO
            (e.g., 'transport_photos/<user_id>_<uuid>.<ext>').

    Raises:
        S3Error: If the upload to MinIO fails due to server issues or
            invalid configuration.
        ValueError: If the file has no extension.
    """
    # Generate object name with user ID and UUID
    file_ext = file.filename.split(".")[-1]
    if not file_ext:
        raise ValueError("File has no extension")
    object_name = f"transport_photos/{transport_id}_{uuid4().hex}.{file_ext}"

    # Upload file to MinIO
    return await upload_file_to_minio(file, object_name)
