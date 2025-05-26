from app.db.session import engine
from app.db.base import Base
from app.models import (
    User, Client, Carrier,
    Order, Comment, OrderHistory,
    Transport, Schedule,
    Cities, Route,
    Docs, ExtraService,
    Newsletter,
)

def init_db():
    Base.metadata.create_all(bind=engine.sync_engine)