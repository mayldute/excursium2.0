from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class Newsletter(Base):
    __tablename__ = 'newsletters'

    id = Column(Integer, primary_key=True, index=True)
    header = Column(String(255))
    text = Column(Text)