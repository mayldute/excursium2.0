from fastapi import FastAPI
from app.api.v1.client import router as client_router
from app.api.v1.carrier import router as carrier_router
from app.api.v1.user import router as user_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks.cleanup import delete_unactivated_users

app = FastAPI()

app.include_router(client_router)
app.include_router(carrier_router)
app.include_router(user_router)

scheduler = AsyncIOScheduler()
scheduler.add_job(delete_unactivated_users, "interval", hours=1)
scheduler.start()