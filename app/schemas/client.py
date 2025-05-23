from pydantic import BaseModel, model_validator, Field

from app.schemas import UserCreate, UserResponse, UserUpdate
from app.utils import validate_individual_client, validate_legal_minimal, validate_legal_entity
from app.models import ClientTypeEnum, LegalTypeEnum

class ClientCreate(BaseModel):
    client_type: ClientTypeEnum = Field(..., description="Type of client: individual or legal entity", example="IND")
    legal_type: LegalTypeEnum | None = Field(default=None, description="Legal type if client is a legal entity", example="LLC")
    custom_type: str | None = Field(default=None, description="Custom legal type if 'Other' is selected", example="Non-standard entity")
    company_name: str | None = Field(default=None, description="Name of the company (for legal entities)", example="LLC Example")
    inn: str | None = Field(default=None, description="Taxpayer Identification Number", example="1234567890")
    kpp: str | None = Field(default=None, description="Tax Registration Reason Code", example="123456789")
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
    id: int = Field(..., description="Client ID", example=1)
    client_type: ClientTypeEnum = Field(..., description="Client type", example="IND")
    legal_type: LegalTypeEnum = Field(..., description="Legal type", example="LLC")
    custom_type: str = Field(..., description="Custom legal type if applicable", example="Non-standard entity")
    company_name: str = Field(..., description="Company name", example="LLC Example")
    inn: str = Field(..., description="INN", example="1234567890")
    kpp: str = Field(..., description="KPP", example="123456789")
    ogrn: str = Field(..., description="OGRN", example="1234567890123")
    current_account: str = Field(..., description="Current account", example="40702810900000000001")
    corresp_account: str = Field(..., description="Correspondent account", example="30101810400000000225")
    bik: str = Field(..., description="Bank Identifier Code", example="044525225")
    oktmo: str = Field(..., description="OKTMO code", example="45382000")
    address: str = Field(..., description="Legal address", example="Moscow, Lenina St., 1")
    user: UserResponse

    class Config:
        from_attributes = True

class ClientUpdate(BaseModel):
    client_type: ClientTypeEnum | None = Field(default=None, description="Type of client", example="IND")
    legal_type: LegalTypeEnum | None = Field(default=None, description="Legal type", example="LLC")
    custom_type: str | None = Field(default=None, description="Custom legal type if 'Other' is selected", example="Non-standard entity")
    company_name: str | None = Field(default=None, description="Name of the company (for legal entities)", example="LLC Example")
    inn: str | None = Field(default=None, description="Taxpayer Identification Number", example="1234567890")
    kpp: str | None = Field(default=None, description="Tax Registration Reason Code", example="123456789")
    ogrn: str | None = Field(default=None, description="OGRN", example="1234567890123")
    current_account: str | None = Field(default=None, description="Current account", example="40702810900000000001")
    corresp_account: str | None = Field(default=None, description="Correspondent account", example="30101810400000000225")
    bik: str | None = Field(default=None, description="Bank Identifier Code", example="044525225")
    oktmo: str | None = Field(default=None, description="OKTMO code", example="45382000")
    address: str | None = Field(default=None, description="Legal address", example="Moscow, Lenina St., 1")
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

