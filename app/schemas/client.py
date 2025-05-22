from pydantic import BaseModel, model_validator

from app.schemas import UserCreate, UserResponse, UserUpdate
from app.utils import validate_individual_client, validate_legal_minimal, validate_legal_entity
from app.models import ClientTypeEnum, LegalTypeEnum

class ClientCreate(BaseModel):
    client_type: ClientTypeEnum
    legal_type: LegalTypeEnum | None = None
    custom_type: str | None = None
    company_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    user: UserCreate

    @model_validator(mode="before")
    def validate_client_data(cls, values):
        client_type = values.get("client_type")
        legal_type = values.get("legal_type")
        user = values.get("user", {})

        if client_type == "IND":
            # Validate individual client fields
            validate_individual_client(user, legal_type)
        elif client_type == "LEG":
            # Validate company name, INN, KPP, and legal type
            validate_legal_minimal(values)
        else:
            raise ValueError("Invalid client_type. Must be 'IND' or 'LEG'.")

        return values

class ClientResponse(BaseModel):
    id: int
    client_type: ClientTypeEnum
    legal_type: LegalTypeEnum 
    custom_type: str     # Custom type for other legal types
    company_name: str 
    inn: str 
    kpp: str 
    ogrn: str 
    current_account: str 
    corresp_account: str 
    bik: str 
    oktmo: str 
    address: str 
    user: UserResponse

    class Config:
        from_attributes = True

class ClientUpdate(BaseModel):
    client_type: ClientTypeEnum | None = None
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
    def validate_client_update(cls, values):
        client_type = values.get("client_type")
        legal_type = values.get("legal_type")
        user = values.get("user", {})

        if client_type == "IND":
            # Validate individual client fields
            validate_individual_client(user, legal_type)
        
        if client_type == "LEG":
            # Validate legal entity fields
            validate_legal_entity(values)

        return values

