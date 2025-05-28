from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator, Field

from app.utils import validate_transport_data

class TransportCreate(BaseModel):
    name: str = Field(..., description="Unique name of the transport", example="Bus-123")
    brand: str = Field(..., description="Transport brand", example="Mercedes")
    model: str = Field(..., description="Transport model", example="Sprinter 519")
    year: int = Field(..., description="Year of manufacture (4-digit)", example=2020)
    n_desk: int = Field(..., description="Number of desk seats", example=4)
    n_seat: int = Field(..., description="Total number of seats", example=16)
    luggage: bool = Field(False, description="Whether luggage space is available")
    wifi: bool = Field(False, description="Whether Wi-Fi is available")
    tv: bool = Field(False, description="Whether a TV is available")
    air_conditioning: bool = Field(False, description="Whether air conditioning is available")
    toilet: bool = Field(False, description="Whether a toilet is available")

    @model_validator(mode="before")
    def validate_data(cls, values):
        """Validate year, desk, and seat counts before creating a transport."""
        validate_transport_data(values)
        return values
    
class TransportUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated name of the transport", example="Bus-456")
    brand: Optional[str] = Field(None, description="Updated brand", example="Ford")
    model: Optional[str] = Field(None, description="Updated model", example="Transit Custom")
    year: Optional[int] = Field(None, description="Updated year of manufacture", example=2022)
    n_desk: Optional[int] = Field(None, description="Updated number of desk seats", example=6)
    n_seat: Optional[int] = Field(None, description="Updated number of total seats", example=20)
    luggage: Optional[bool] = Field(None, description="Update luggage availability")
    wifi: Optional[bool] = Field(None, description="Update Wi-Fi availability")
    tv: Optional[bool] = Field(None, description="Update TV availability")
    air_conditioning: Optional[bool] = Field(None, description="Update air conditioning availability")
    toilet: Optional[bool] = Field(None, description="Update toilet availability")

    @model_validator(mode="before")
    def validate_data(cls, values):
        """Validate year, desk, and seat counts before creating a transport."""
        validate_transport_data(values)
        return values

class TransportResponse(BaseModel):
    id: int = Field(..., description="Transport ID", example=1)
    name: str = Field(..., description="Name of the transport", example="Bus-123")
    brand: str = Field(..., description="Transport brand", example="Mercedes")
    model: str = Field(..., description="Transport model", example="Sprinter 519")
    year: int = Field(..., description="Year of manufacture", example=2020)
    n_desk: int = Field(..., description="Number of desk seats", example=4)
    n_seat: int = Field(..., description="Number of total seats", example=16)
    luggage: bool = Field(..., description="Luggage availability")
    wifi: bool = Field(..., description="Wi-Fi availability")
    tv: bool = Field(..., description="TV availability")
    air_conditioning: bool = Field(..., description="Air conditioning availability")
    toilet: bool = Field(..., description="Toilet availability")
    photo: str = Field(..., description="Transport photo URL", example="https://yourdomain.com/media/transport_photos/bus-123.jpg")
    rating: float = Field(..., description="Average rating of the transport", example=4.5)

    model_config = ConfigDict(from_attributes=True)
