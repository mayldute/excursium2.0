from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.client import ClientCreate
from app.dependencies.get_db import get_db
from app.services.client import register_client_service

router = APIRouter(prefix="/auth", tags=["[auth] client"])

@router.post("/register/client", summary="Client registration (individual/legal entity)")
async def register_client(
    payload: ClientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await register_client_service(payload, db, request)