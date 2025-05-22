from pydantic import BaseModel, model_validator

from app.schemas import UserCreate, UserResponse, UserUpdate
from app.utils import validate_legal_minimal, validate_legal_entity
from app.models import LegalTypeEnum, DocTypeEnum, DocStatusEnum

class CarrierCreate(BaseModel):
    legal_type: LegalTypeEnum
    custom_type: str | None = None   # Custom type for other legal types
    company_name: str
    inn: str
    kpp: str
    user: UserCreate

    @model_validator(mode="before")
    def validate_carrier_data(cls, values):
        # Validate company name, INN, KPP, and legal type
        validate_legal_minimal(values)
        
        return values
    
class CarrierResponse(BaseModel):
    id: int
    legal_type: LegalTypeEnum
    custom_type: str 
    company_name: str
    inn: str
    kpp: str
    ogrn: str 
    current_account: str 
    corresp_account: str 
    bik: str
    oktmo: str 
    address: str 
    rating: float 
    user: UserResponse

    class Config:
        from_attributes = True

class CarrierUpdate(BaseModel):
    legal_type: LegalTypeEnum | None = None
    custom_type: str | None = None
    company_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    ogrn: str | None = None
    current_account: str | None = None
    corresp_account: str | None = None
    bik: str | None = None
    oktmo: str | None = None
    address: str | None = None
    user: UserUpdate | None = None

    @model_validator(mode="before")
    def validate_carrier_update(cls, values):
        # Validate all carrier fields
        validate_legal_entity(values)

        return values
    
class CarrierDocsResponse(BaseModel):
    id: int
    carrier_id: int
    doc_type: DocTypeEnum
    file_path: str
    status: DocStatusEnum

    class Config:
        from_attributes = True
