from fastapi import FastAPI
from app.api.v1.client import router as client_router
from app.api.v1.carrier import router as carrier_router
from app.api.v1.user import router as user_router

app = FastAPI()

app.include_router(client_router)
app.include_router(carrier_router)
app.include_router(user_router)