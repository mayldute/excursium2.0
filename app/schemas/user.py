from pydantic import BaseModel, EmailStr, model_validator, StringConstraints
from typing import Optional, Annotated

PhoneNumberStr = Annotated[
    str,
    StringConstraints(
        pattern=r'^\+\d{10,15}$',
        strip_whitespace=True,
        min_length=11,
        max_length=16 
    )
]

class UserCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[PhoneNumberStr] = None
    password1: str
    password2: str

    @model_validator(mode="before")
    def check_passwords(cls, values):
        password = values.get("password1")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit.")
    
        if values.get("password1") != values.get("password2"):
            raise ValueError("Passwords do not match")

        return values
    
class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str