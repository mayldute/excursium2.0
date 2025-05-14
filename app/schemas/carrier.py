from pydantic import BaseModel, model_validator
from typing import Optional
from app.schemas.user import UserCreate

class CarrierCreate(BaseModel):
    carrier_type: str
    custom_type: Optional[str] = None
    company_name: str
    inn: str
    kpp: str
    user: UserCreate

    @model_validator(mode="before")
    def validate_client_data(cls, values):
        carrier_type = values.get("carrier_type")
        custom_type = values.get("custom_type")

        if carrier_type == "OTH" and not custom_type:
            raise ValueError("Custom type is required when carrier_type is 'OTH'.")
        
        if carrier_type != "OTH" and custom_type:
            raise ValueError("Custom type should not be provided when carrier_type is not 'OTH'.")
            
        if carrier_type == "IE":
            if len(values.get("inn", "")) != 12:
                    raise ValueError("INN must be 12 characters for IE.")
        else:
            if len(values.get("inn", "")) != 10:
                raise ValueError("INN must be 10 characters")
        
        if len(values.get("kpp", "")) != 9:
            raise ValueError("KPP must be 10 characters")
        
        return values
    
