from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    TransportCreate
)

from app.dependencies.get_db import get_db
from app.dependencies.context import get_common_context, CommonContext
from app.services.transport import (
    create_transport_service,
)

# Initialize API router for transport routes
router = APIRouter(prefix="/transport", tags=["[transport] transport"])

@router.post("/transport", summary="Create new transport", status_code=201)
async def create_trancport(
    payload: TransportCreate,
    context: CommonContext = Depends(get_common_context)
):
    return await create_transport_service(payload, context.current_user, context.db)
