from typing import Optional
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, model_validator, Field

from app.utils import validate_transport_data
from app.models import ScheduleReasonEnum

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

class ScheduleCreate(BaseModel):
    transport_id: int = Field(..., description="ID of the transport for the schedule", example=1)
    start_time: datetime = Field(..., description="Start time of the schedule in ISO format", example="2023-10-01T08:00:00Z")
    end_time: datetime = Field(..., description="End time of the schedule in ISO format", example="2023-10-01T10:00:00Z")
    reason: ScheduleReasonEnum = Field(..., description="Reason for the schedule", example="TECHNICAL")

    @model_validator(mode="after")
    def validate_schedule(cls, model):
        """Validate schedule start and end times."""
        now = datetime.now(timezone.utc)

        if model.start_time < now:
            raise ValueError("Start time cannot be in the past")
        if model.end_time <= model.start_time:
            raise ValueError("End time must be after start time")
        
        return model