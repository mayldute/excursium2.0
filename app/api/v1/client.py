from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    ClientCreate, 
    ClientResponse, 
    ClientUpdate
)

from app.dependencies.get_db import get_db
from app.dependencies.context import get_common_context, CommonContext
from app.services.client import (
    register_client_service, 
    get_client_service, 
    update_client_service, 
    delete_client_service
)

# Initialize API router for client routes
router = APIRouter(prefix="/auth", tags=["[auth] client"])

@router.post("/client", summary="Client registration (individual/legal entity)", status_code=201)
async def register_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    # Register client using service
    return await register_client_service(payload, db)


@router.get("/client/{client_id}", response_model=ClientResponse, summary="Get client by ID", status_code=200)
async def get_client(
    client_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Fetch client using service
    return await get_client_service(client_id, context.current_user, context.db)


@router.patch("/client/{client_id}", response_model=ClientResponse, summary="Update client by ID", status_code=200)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    context: CommonContext = Depends(get_common_context)
):
    # Update client using service
    return await update_client_service(client_id, payload, context.current_user, context.db)


@router.delete("/client/{client_id}", summary="Delete client by ID", status_code=204)
async def delete_client(
    client_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Delete client using service
    return await delete_client_service(client_id, context.current_user, context.db)

