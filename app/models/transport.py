from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Transport(Base):
    __tablename__ = 'transports'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    brand = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    n_desk = Column(Integer)
    n_seat = Column(Integer)
    photo = Column(String)
    luggage = Column(Boolean, default=False)
    wifi = Column(Boolean, default=False)
    tv = Column(Boolean, default=False)
    air_conditioning = Column(Boolean, default=False)
    toilet = Column(Boolean, default=False)
    price = Column(Integer)
    rating = Column(Integer, default=0)

    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    carrier = relationship("Carrier", back_populates="transports")
    route_id = Column(Integer, ForeignKey("routes.id"))
    route = relationship("Route", back_populates="transports")
    orders = relationship("Order", back_populates="transport", uselist=True)
    schedules = relationship("Schedule", back_populates="transport", uselist=True)

class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True, index=True)
    id_from = Column(Integer, ForeignKey("cities.id"), nullable=False)
    id_to = Column(Integer, ForeignKey("cities.id"), nullable=False)

    from_city = relationship("Cities", back_populates="routes_from", foreign_keys=[id_from])
    to_city = relationship("Cities", back_populates="routes_to", foreign_keys=[id_to])
    transports = relationship("Transport", back_populates="route", uselist=True)
    orders = relationship("Order", back_populates="route", uselist=True)

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, index=True)
    trip_start = Column(DateTime)
    trip_end = Column(DateTime)

    id_transport = Column(Integer, ForeignKey('transports.id'))
    transport = relationship("Transport", back_populates="schedules")



