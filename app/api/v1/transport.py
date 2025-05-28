from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    TransportCreate,
    TransportUpdate,
    TransportResponse,
)

from app.dependencies.get_db import get_db
from app.dependencies.context import get_common_context, CommonContext
from app.services.transport import (
    create_transport_service,
    update_transport_service,
    get_transports_by_carrier_id_service,
    delete_transport_service,
    upload_transport_photo_service,
)

# Initialize API router for transport routes
router = APIRouter(prefix="/transport", tags=["[transport] transport"])

@router.post("/create", response_model=TransportResponse, summary="Create new transport", status_code=201)
async def create_trancport(
    payload: TransportCreate,
    context: CommonContext = Depends(get_common_context)
):
    # Create a new transport using the service
    return await create_transport_service(payload, context.current_user, context.db)


@router.patch("/{transport_id}", response_model=TransportResponse, summary="Update transport by ID", status_code=200)
async def update_transport(
    transport_id: int,
    payload: TransportUpdate,  
    context: CommonContext = Depends(get_common_context)
):
    # Update the transport using the service
    return await update_transport_service(transport_id, payload, context.current_user, context.db)


@router.get("/{carrier_id}", response_model=List[TransportResponse], summary="Get transport by carrier ID", status_code=200)
async def get_transport_by_carrier_id(
    carrier_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Fetch transports by carrier ID using the service
    return await get_transports_by_carrier_id_service(carrier_id, context.current_user, context.db)

@router.delete("/{transport_id}", summary="Delete transport by ID", status_code=204)
async def delete_transport(
    transport_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Delete the transport using the service
    return await delete_transport_service(transport_id, context.current_user, context.db)


@router.patch("/photo/{transport_id}", summary="Update transport photo", status_code=200)
async def update_transport_photo(
    transport_id: int,
    file: UploadFile = File(...),
    context: CommonContext = Depends(get_common_context)
):
    # Upload the transport photo using the service
    return await upload_transport_photo_service(transport_id, file, context.current_user, context.db)