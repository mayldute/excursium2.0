from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DocTypeEnum
from app.schemas import (
    CarrierCreate,
    CarrierResponse,
    CarrierUpdate,
    CarrierDocsResponse
)

from app.dependencies.get_db import get_db
from app.dependencies.context import get_common_context, CommonContext
from app.services.carrier import (
    register_carrier_service,
    get_carrier_service,
    update_carrier_service,
    delete_carrier_service,
    upload_carrier_docs_service,
    get_carrier_docs_service
)

# Initialize API router for carrier routes
router = APIRouter(prefix="/auth", tags=["[auth] carrier"])


@router.post("/carrier", summary="Carrier registration", status_code=201)
async def register_carrier(
    payload: CarrierCreate,
    db: AsyncSession = Depends(get_db)
):
    # Register carrier using service
    return await register_carrier_service(payload, db)


@router.get(
    "/carrier/{carrier_id}",
    response_model=CarrierResponse,
    summary="Get carrier by ID",
    status_code=200
)
async def get_carrier(
    carrier_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Fetch carrier using service
    return await get_carrier_service(
        carrier_id, context.current_user, context.db
    )


@router.patch(
    "/carrier/{carrier_id}",
    response_model=CarrierResponse,
    summary="Update carrier by ID",
    status_code=200
)
async def update_carrier(
    carrier_id: int,
    payload: CarrierUpdate,
    context: CommonContext = Depends(get_common_context)
):
    # Update carrier using service
    return await update_carrier_service(
        carrier_id, payload, context.current_user, context.db
    )


@router.delete(
    "/carrier/{carrier_id}",
    summary="Soft delete carrier by ID",
    status_code=204
)
async def delete_carrier(
    carrier_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Delete carrier using service
    return await delete_carrier_service(
        carrier_id, context.current_user, context.db
    )


@router.post(
    "/carrier/upload-docs/{carrier_id}",
    summary="Upload one or more documents for a specific carrier",
    status_code=201
)
async def upload_docs(
    carrier_id: int,
    doc_type: DocTypeEnum = Form(...),
    files: List[UploadFile] = File(...),
    context: CommonContext = Depends(get_common_context)
):
    # Upload documents using service
    return await upload_carrier_docs_service(
        carrier_id, files, doc_type, context.current_user, context.db
    )


@router.get(
    "/carrier/docs/{carrier_id}",
    response_model=List[CarrierDocsResponse],
    summary="Get documents for carrier",
    status_code=200
)
async def get_docs(
    carrier_id: int,
    context: CommonContext = Depends(get_common_context)
):
    # Fetch carrier documents using service
    return await get_carrier_docs_service(
        carrier_id, context.current_user, context.db
    )
