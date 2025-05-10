from fastapi import FastAPI
from app.api.v1.client import router as client_router
from app.api.v1.carrier import router as carrier_router

app = FastAPI()

app.include_router(client_router)
app.include_router(carrier_router)