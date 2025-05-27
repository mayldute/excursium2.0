from pydantic import BaseModel, EmailStr, model_validator, StringConstraints, Field
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
    first_name: str | None = Field(default=None, description="User's first name", example="John")
    last_name: str | None = Field(default=None, description="User's last name", example="Doe")
    middle_name: str | None = Field(default=None, description="User's middle name", example="Michael")
    email: EmailStr = Field(..., description="User's email address", example="john.doe@example.com")
    phone_number: PhoneNumberStr | None = Field(default=None, description="User's phone number in international format", example="+12345678901")
    is_oauth_user: bool = Field(default=False, description="Indicates if the user is created via OAuth", example=False)
    password1: str = Field(..., description="User's password", example="StrongPass123!")
    password2: str = Field(..., description="Password confirmation", example="StrongPass123!")

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
    email: EmailStr = Field(..., description="User's email", example="john.doe@example.com")
    password: str = Field(..., description="User's password", example="StrongPass123!")

class UserResponse(BaseModel):
    id: int = Field(..., description="User ID", example=1)
    first_name: str = Field(..., description="First name", example="John")
    last_name: str = Field(..., description="Last name", example="Doe")
    middle_name: str = Field(..., description="Middle name", example="Michael")
    email: EmailStr = Field(..., description="Email", example="john.doe@example.com")
    phone_number: PhoneNumberStr = Field(..., description="Phone number", example="+12345678901")
    photo: str = Field(..., description="Path to user photo", example="user_photos/photo.jpg")
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, description="First name", example="John")
    last_name: str | None = Field(default=None, description="Last name", example="Doe")
    middle_name: str | None = Field(default=None, description="Middle name", example="Michael")
    phone_number: Optional[PhoneNumberStr] = Field(default=None, description="Phone number", example="+12345678901")
    photo: Optional[str] = Field(default=None, description="Photo path", example="user_photos/photo.jpg")

class CompleteRegistration(BaseModel):
    first_name: str = Field(..., description="First name", example="John")  
    last_name: str = Field(..., description="Last name", example="Doe")
    middle_name: str | None = Field(default=None, description="Middle name", example="Michael")  
    phone_number: PhoneNumberStr = Field(..., description="Phone number", example="+12345678901")
    
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token", example="eyJhbGciOiJIUzI1...")
    refresh_token: str = Field(..., description="JWT refresh token", example="eyJhbGciOiJIUzI1...")
    token_type: str = Field(..., description="Token type", example="bearer")

class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., description="Current password", example="OldPass123!")
    new_password: str = Field(..., description="New password", example="NewStrongPass456!")

class EmailRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address", example="user@example.com")