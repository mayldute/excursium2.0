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

PasswordStr = Annotated[
    str,
    StringConstraints(
        pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$',
        min_length=8,
        max_length=128
    )
]

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    phone_number: PhoneNumberStr
    password1: PasswordStr
    password2: PasswordStr

    @model_validator(mode="before")
    def check_passwords_match(cls, values):
        if values.get("password1") != values.get("password2"):
            raise ValueError("Passwords do not match")
        return values
    