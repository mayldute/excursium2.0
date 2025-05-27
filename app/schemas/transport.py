from pydantic import BaseModel

class TransportCreate(BaseModel):
    name: str
    brand: str
    model: str
    year: int
    n_desk: int
    n_seat: int
    photo: str 
    luggage: bool = False
    wifi: bool = False
    tv: bool = False
    air_conditioning: bool = False
    toilet: bool = False
    carrier_id: int
