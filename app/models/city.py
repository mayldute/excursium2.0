from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class Cities(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)

    routes_from = relationship("Route", back_populates="from_city", foreign_keys='Route.id_from')
    routes_to = relationship("Route", back_populates="to_city", foreign_keys='Route.id_to')



