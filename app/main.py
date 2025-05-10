from fastapi import FastAPI
from app.api.v1.client import router as client_router

app = FastAPI()

app.include_router(client_router)
