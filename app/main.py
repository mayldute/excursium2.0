from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.api.v1.client import router as client_router
from app.api.v1.carrier import router as carrier_router
from app.api.v1.user import router as user_router
from app.tasks.cleanup import (
    delete_unactivated_users, 
    delete_deleted_users, 
    delete_unchanged_emails,
    delete_oauth_state,
)

# Initialize FastAPI application
app = FastAPI(debug=settings.app.debug)

# Register API routers
app.include_router(client_router)
app.include_router(carrier_router)
app.include_router(user_router)

# Initialize and configure scheduler for background tasks
scheduler = AsyncIOScheduler()
scheduler.add_job(delete_oauth_state, "interval", minutes=10)      # Clean up expired OAuth states every 10 minutes
scheduler.add_job(delete_unchanged_emails, "interval", minutes=30)  # Clean up unconfirmed email changes every 30 minutes
scheduler.add_job(delete_unactivated_users, "interval", hours=1)    # Remove unactivated users every hour
scheduler.add_job(delete_deleted_users, "interval", days=1)         # Delete permanently removed users daily
scheduler.start()