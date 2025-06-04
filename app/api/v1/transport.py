from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    TransportCreate,
    TransportUpdate,
    TransportResponse,
    ScheduleCreate,
    TransportFilter,
    TransportFilterResponse,
)

from app.dependencies.get_db import get_db
from app.dependencies.context import get_common_context, CommonContext
from app.services.transport import (
    create_transport_service,
    update_transport_service,
    get_transports_by_carrier_id_service,
    delete_transport_service,
    upload_transport_photo_service,
    add_route_to_transport_service,
    get_transport_routes_service,
    delete_transport_route_service,
    add_transport_schedule_service,
    get_transport_schedules_service,
    delete_transport_schedules_service,
    filter_transports_service,
    get_transport_by_id_service,
)

# Initialize API router for transport routes
router = APIRouter(prefix="/transport", tags=["[transport] transport"])

@router.get("/search", response_model=List[TransportFilterResponse], summary="Search transports", status_code=200)
async def search_transports(
    filters: TransportFilter = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # Search transports based on provided filters
    return await filter_transports_service(filters, db)


@router.get("/search/{transport_id}", response_model=TransportFilterResponse, summary="Search transports by carrier ID", status_code=200)
async def search_transport_by_id(
    transport_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Fetch transport by ID using the service
    return await get_transport_by_id_service(transport_id, db)


@router.post("/create", response_model=TransportResponse, summary="Create new transport", status_code=201)
async def create_trancport(
    payload: TransportCreate,
    context: CommonContext = Depends(get_common_context)
):
    # Create a new transport using the service
    return await create_transport_service(payload, context.current_user, context.db)


@router.get("/{carrier_id}", response_model=List[TransportResponse], summary="Get transport by carrier ID", status_code=200)
async def get_transport_by_carrier_id(
    carrier_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Fetch transports by carrier ID using the service
    return await get_transports_by_carrier_id_service(carrier_id, context.current_user, context.db)


@router.patch("/{transport_id}", response_model=TransportResponse, summary="Update transport by ID", status_code=200)
async def update_transport(
    transport_id: int,
    payload: TransportUpdate,  
    context: CommonContext = Depends(get_common_context)
):
    # Update the transport using the service
    return await update_transport_service(transport_id, payload, context.current_user, context.db)


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


@router.post("/add_route/{transport_id}", summary="Add route to transport", status_code=201)
async def add_route_to_transport(
    transport_id: int,
    id_from: int, 
    id_to: int, 
    min_price: float, 
    max_price: float,
    context: CommonContext = Depends(get_common_context)
):
    # Add a route to the transport using the service
    return await add_route_to_transport_service(transport_id, id_from, id_to, min_price, max_price, context.current_user, context.db)

@router.get("/routes/{transport_id}", summary="Get routes by transport ID", status_code=200)
async def get_routes_by_transport_id(
    transport_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Fetch routes by transport ID using the service
    return await get_transport_routes_service(transport_id, context.current_user, context.db)


@router.delete("/route/{transport_id}/{route_id}", summary="Delete route from transport", status_code=204)
async def delete_route_from_transport(
    transport_id: int,
    route_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Delete a route from the transport using the service
    return await delete_transport_route_service(transport_id, route_id, context.current_user, context.db)


@router.post("/schedule/", summary="Add schedule to transport", status_code=201)
async def add_schedule_to_transport(
    payload: ScheduleCreate,
    context: CommonContext = Depends(get_common_context)
):
    return await add_transport_schedule_service(payload, context.current_user, context.db)


@router.get("/schedule/{transport_id}", summary="Get schedules by transport ID", status_code=200)
async def get_schedules_by_transport_id(
    transport_id: int,
    context: CommonContext = Depends(get_common_context)
):
    return await get_transport_schedules_service(transport_id, context.current_user, context.db)


@router.delete("/schedule/{schedule_id}", summary="Delete schedule from transport", status_code=204)
async def delete_schedule_from_transport(
    schedule_id: int,
    context: CommonContext = Depends(get_common_context)
):
    return await delete_transport_schedules_service(schedule_id, context.current_user, context.db)
