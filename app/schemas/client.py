from pydantic import BaseModel, model_validator
from typing import Optional
from app.schemas.user import UserCreate

class ClientCreate(BaseModel):
    client_type: str
    legal_type: Optional[str] = None
    company_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    user: UserCreate

    @model_validator(mode="before")
    def validate_client_data(cls, values):
        client_type = values.get("client_type")
        legal_type = values.get("legal_type")
        custom_type = values.get("custom_type")
        user = values.get("user", {})

        if client_type == "IND":
            required_user_fields = ['first_name', 'last_name', 'phone_number']
            missing = [f for f in required_user_fields if not user.get(f)]
            if missing:
                raise ValueError(f"Missing fields for individual client: {missing}")

            if legal_type is not None:
                raise ValueError("Legal type must be empty for individual clients.")

        elif client_type == "LEG":
            required_fields = ["company_name", "inn", "kpp", "legal_type"]
            missing = [f for f in required_fields if not values.get(f)]
            if missing:
                raise ValueError(f"Missing fields for legal entity: {missing}")

            if legal_type == "OTH" and not custom_type:
                raise ValueError("Custom type is required when legal_type is 'OTH'.")

            if legal_type == "IE":
                if len(values.get("inn", "")) != 12:
                    raise ValueError("INN must be 12 characters for IE.")
            else:
                if len(values.get("inn", "")) != 10:
                    raise ValueError("INN must be 10 characters for other legal types.")

            if len(values.get("kpp", "")) != 9:
                raise ValueError("KPP must be 9 characters long.")
        else:
            raise ValueError("Invalid client_type. Must be 'IND' or 'LEG'.")

        return values
    
