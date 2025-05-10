from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserLogin, Token
from app.dependencies.get_db import get_db
from app.services.user import authenticate_user

router = APIRouter(prefix="/auth", tags=["[auth] user"])

@router.post("/login", summary="User login", response_model=Token)
async def login(
    payload: UserLogin, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await authenticate_user(payload.email, payload.password, db, request)