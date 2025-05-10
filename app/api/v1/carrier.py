from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.carrier import CarrierCreate
from app.dependencies.get_db import get_db
from app.services.carrier import register_carrier_service

router = APIRouter(prefix="/auth", tags=["[auth] carrier"])

@router.post("/register/carrier", summary="Carrier registration")
async def register_client(
    payload: CarrierCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await register_carrier_service(payload, db, request)