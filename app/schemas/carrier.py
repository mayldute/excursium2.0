from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas import UserCreate, UserResponse, UserUpdate
from app.utils import validate_legal_minimal, validate_legal_entity
from app.models import LegalTypeEnum, DocTypeEnum, DocStatusEnum

from pydantic import Field


class CarrierCreate(BaseModel):
    legal_type: LegalTypeEnum = Field(
        ...,
        description="Legal type of the carrier",
        example="LLC"
    )
    custom_type: str | None = Field(
        default=None,
        description="Custom type if legal type is 'Other'",
        example="Sole Proprietor without formal registration"
    )
    company_name: str = Field(
        ...,
        description="Registered company name",
        example="LLC Romashka"
    )
    inn: str = Field(
        ...,
        description="Taxpayer Identification Number",
        example="1234567890"
    )
    kpp: str = Field(
        ...,
        description="Tax Registration Reason Code",
        example="123456789"
    )
    user: UserCreate

    @model_validator(mode="before")
    def validate_carrier_data(cls, values):
        # Validate company name, INN, KPP, and legal type
        validate_legal_minimal(values)

        return values


class CarrierResponse(BaseModel):
    id: int = Field(..., description="Carrier ID", example=1)
    legal_type: LegalTypeEnum = Field(
        ...,
        description="Legal type of the carrier",
        example="LLC"
    )
    custom_type: str | None = Field(
        ...,
        description="Custom type",
        example="Sole Proprietor without formal registration"
    )
    company_name: str = Field(
        ...,
        description="Registered company name",
        example="LLC Romashka"
    )
    inn: str = Field(
        ...,
        description="Taxpayer Identification Number",
        example="1234567890"
    )
    kpp: str = Field(
        ...,
        description="Tax Registration Reason Code",
        example="123456789"
    )
    ogrn: str | None = Field(
        ...,
        description="Primary State Registration Number",
        example="1234567890123"
    )
    current_account: str | None = Field(
        ...,
        description="Current account number",
        example="40702810900000000001"
    )
    corresp_account: str | None = Field(
        ...,
        description="Correspondent account",
        example="30101810400000000225"
    )
    bik: str | None = Field(
        ...,
        description="Bank Identifier Code",
        example="044525225"
    )
    oktmo: str | None = Field(..., description="OKTMO code", example="45382000")
    address: str | None = Field(
        ...,
        description="Legal address",
        example="Moscow, Lenina St., 1"
    )
    rating: float = Field(..., description="Carrier rating", example=4.8)
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class CarrierUpdate(BaseModel):
    legal_type: LegalTypeEnum | None = Field(
        default=None,
        description="Legal type",
        example="LLC"
    )
    custom_type: str | None = Field(
        default=None,
        description="Custom type if legal type is 'Other'",
        example="Sole Proprietor without formal registration"
    )
    company_name: str | None = Field(
        default=None,
        description="Company name",
        example="LLC Romashka"
    )
    inn: str | None = Field(
        default=None,
        description="INN",
        example="1234567890"
    )
    kpp: str | None = Field(
        default=None,
        description="KPP",
        example="123456789"
    )
    ogrn: str | None = Field(
        default=None,
        description="OGRN",
        example="1234567890123"
    )
    current_account: str | None = Field(
        default=None,
        description="Current account",
        example="40702810900000000001"
    )
    corresp_account: str | None = Field(
        default=None,
        description="Correspondent account",
        example="30101810400000000225"
    )
    bik: str | None = Field(
        default=None,
        description="BIK",
        example="044525225"
    )
    oktmo: str | None = Field(
        default=None,
        description="OKTMO",
        example="45382000"
    )
    address: str | None = Field(
        default=None,
        description="Address",
        example="Moscow, Lenina St., 1"
    )
    user: UserUpdate | None = Field(default=None)

    @model_validator(mode="before")
    def validate_carrier_update(cls, values):
        # Validate all carrier fields
        validate_legal_entity(values)

        return values


class CarrierDocsResponse(BaseModel):
    id: int = Field(..., description="Document ID", example=101)
    carrier_id: int = Field(..., description="Associated carrier ID", example=1)
    doc_type: DocTypeEnum = Field(
        ...,
        description="Document type",
        example="LC"
    )
    file_path: str = Field(
        ...,
        description="Path to file in storage",
        example="carrier_docs/license.pdf"
    )
    status: DocStatusEnum = Field(
        ...,
        description="Document status",
        example="PENDING"
    )

    model_config = ConfigDict(from_attributes=True)
