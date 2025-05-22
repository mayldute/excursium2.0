from pydantic import BaseModel, EmailStr, model_validator, StringConstraints
from typing import Optional, Annotated

# Custom type for phone number validation
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
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: EmailStr
    phone_number: PhoneNumberStr | None = None
    password1: str
    password2: str

    @model_validator(mode="before")
    def check_passwords(cls, values):
        """Check if the passwords match and meet complexity requirements."""
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
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str 
    last_name: str
    middle_name: str 
    email: EmailStr
    phone_number: PhoneNumberStr 
    photo: str 
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    phone_number: Optional[PhoneNumberStr] = None
    photo: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class EmailRequest(BaseModel):
    email: EmailStr