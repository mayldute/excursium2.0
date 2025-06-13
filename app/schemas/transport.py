from datetime import datetime, timezone
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    Field,
    ValidationError
)

from app.utils import validate_transport_data
from app.models import ScheduleReasonEnum


class TransportFilter(BaseModel):
    id_from: int = Field(..., description="City from ID", example=1)
    id_to: int = Field(..., description="City to ID", example=2)
    start_time: datetime = Field(
        ...,
        description="Start time",
        example="2025-06-05T08:00:00Z"
    )
    end_time: datetime = Field(
        ...,
        description="End time",
        example="2025-06-05T12:00:00Z"
    )
    n_seat: int = Field(..., gt=0, description="Number of seats", example=10)
    min_price: float = Field(
        ...,
        ge=0,
        description="Minimum price",
        example=100.0
    )
    max_price: float = Field(
        ...,
        ge=0,
        description="Maximum price",
        example=500.0
    )
    luggage: bool | None = Field(None)
    wifi: bool | None = Field(None)
    tv: bool | None = Field(None)
    air_conditioning: bool | None = Field(None)
    toilet: bool | None = Field(None)
    sort_by: Literal["rating", "price"] | None = Field("rating")
    sort_order: Literal["asc", "desc"] | None = Field("desc")

    @model_validator(mode="after")
    def validate_times_and_prices(self) -> "TransportFilter":
        errors = {}

        if self.start_time < datetime.now(timezone.utc):
            errors["start_time"] = "Must be in the future"

        if self.end_time <= self.start_time:
            errors["end_time"] = "Must be after start_time"

        if self.max_price < self.min_price:
            errors["max_price"] = "Must be greater than or equal to min_price"

        if errors:
            raise ValidationError.from_exception_data(
                self.__class__.__name__, [(k, v) for k, v in errors.items()]
            )

        return self


class TransportFilterResponse(BaseModel):
    id: int = Field(..., description="Transport ID", example=1)
    carrier_id: int = Field(
        ...,
        description="ID of the carrier providing the transport",
        example=1
    )
    brand: str = Field(..., description="Transport brand", example="Mercedes")
    model: str = Field(
        ...,
        description="Transport model",
        example="Sprinter 519"
    )
    n_seat: int = Field(..., description="Number of total seats", example=16)
    luggage: bool = Field(..., description="Luggage availability")
    wifi: bool = Field(..., description="Wi-Fi availability")
    tv: bool = Field(..., description="TV availability")
    air_conditioning: bool = Field(
        ...,
        description="Air conditioning availability"
    )
    toilet: bool = Field(..., description="Toilet availability")
    photo: str = Field(
        ...,
        description="Transport photo URL",
        example="https://yourdomain.com/media/transport_photos/bus-123.jpg"
    )
    rating: float = Field(
        ...,
        description="Average rating of the transport",
        example=4.5
    )
    min_price: float = Field(
        ...,
        description="Minimum price of the transport",
        example=100.0
    )
    max_price: float = Field(
        ...,
        description="Maximum price of the transport",
        example=500.0
    )

    model_config = ConfigDict(from_attributes=True)


class TransportCreate(BaseModel):
    name: str = Field(
        ...,
        description="Unique name of the transport",
        example="Bus-123"
    )
    brand: str = Field(..., description="Transport brand", example="Mercedes")
    model: str = Field(
        ...,
        description="Transport model",
        example="Sprinter 519"
    )
    year: int = Field(
        ...,
        description="Year of manufacture (4-digit)",
        example=2020
    )
    n_seat: int = Field(..., description="Total number of seats", example=16)
    luggage: bool = Field(
        False,
        description="Whether luggage space is available"
    )
    wifi: bool = Field(False, description="Whether Wi-Fi is available")
    tv: bool = Field(False, description="Whether a TV is available")
    air_conditioning: bool = Field(
        False,
        description="Whether air conditioning is available"
    )
    toilet: bool = Field(False, description="Whether a toilet is available")

    @model_validator(mode="before")
    def validate_data(cls, values):
        """Validate year, desk, and seat counts before creating a transport."""
        validate_transport_data(values)
        return values


class TransportUpdate(BaseModel):
    name: str | None = Field(
        None,
        description="Updated name of the transport",
        example="Bus-456"
    )
    brand: str | None = Field(None, description="Updated brand", example="Ford")
    model: str | None = Field(
        None,
        description="Updated model",
        example="Transit Custom"
    )
    year: int | None = Field(
        None,
        description="Updated year of manufacture",
        example=2022
    )
    n_seat: int | None = Field(
        None,
        description="Updated number of total seats",
        example=20
    )
    luggage: bool | None = Field(
        None,
        description="Update luggage availability"
    )
    wifi: bool | None = Field(None, description="Update Wi-Fi availability")
    tv: bool | None = Field(None, description="Update TV availability")
    air_conditioning: bool | None = Field(
        None,
        description="Update air conditioning availability"
    )
    toilet: bool | None = Field(None, description="Update toilet availability")

    @model_validator(mode="before")
    def validate_data(cls, values):
        """Validate year, desk, and seat counts before creating a transport."""
        validate_transport_data(values)
        return values


class TransportResponse(BaseModel):
    id: int = Field(..., description="Transport ID", example=1)
    name: str = Field(
        ...,
        description="Name of the transport",
        example="Bus-123"
    )
    brand: str = Field(..., description="Transport brand", example="Mercedes")
    model: str = Field(
        ...,
        description="Transport model",
        example="Sprinter 519"
    )
    year: int = Field(..., description="Year of manufacture", example=2020)
    n_seat: int = Field(..., description="Number of total seats", example=16)
    luggage: bool = Field(..., description="Luggage availability")
    wifi: bool = Field(..., description="Wi-Fi availability")
    tv: bool = Field(..., description="TV availability")
    air_conditioning: bool = Field(
        ...,
        description="Air conditioning availability"
    )
    toilet: bool = Field(..., description="Toilet availability")
    photo: str = Field(
        ...,
        description="Transport photo URL",
        example="https://yourdomain.com/media/transport_photos/bus-123.jpg"
    )
    rating: float = Field(
        ...,
        description="Average rating of the transport",
        example=4.5
    )

    model_config = ConfigDict(from_attributes=True)


class ScheduleCreate(BaseModel):
    transport_id: int = Field(
        ...,
        description="ID of the transport for the schedule",
        example=1
    )
    start_time: datetime = Field(
        ...,
        description="Start time of the schedule in ISO format",
        example="2023-10-01T08:00:00Z"
    )
    end_time: datetime = Field(
        ...,
        description="End time of the schedule in ISO format",
        example="2023-10-01T10:00:00Z"
    )
    reason: ScheduleReasonEnum = Field(
        ...,
        description="Reason for the schedule",
        example="TECHNICAL"
    )

    @model_validator(mode="after")
    def validate_schedule(cls, model):
        """Validate schedule start and end times."""
        now = datetime.now(timezone.utc)

        if model.start_time < now:
            raise ValueError("Start time cannot be in the past")
        if model.end_time <= model.start_time:
            raise ValueError("End time must be after start time")

        return model
