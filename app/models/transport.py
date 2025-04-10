from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, func
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.order import Comment
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
    rating = Column(Float, default=0.0)

    carrier_id = Column(Integer, ForeignKey("carriers.id", ondelete="CASCADE"))
    carrier = relationship("Carrier", back_populates="transports")
    orders = relationship("Order", back_populates="transport", lazy='dynamic', uselist=True)
    schedules = relationship("Schedule", back_populates="transport", lazy='dynamic', uselist=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"))
    route = relationship("Route", back_populates="transports")
    comments = relationship("Comment", back_populates="transport", lazy='dynamic', uselist=True)
    transport_routes = relationship("TransportRoute", back_populates="transport")

    @staticmethod
    def update_transport_rating(db, transport_id: int):
        avg_rating = db.query(func.avg(Comment.rating))\
            .filter(Comment.transport_id == transport_id)\
            .scalar()

        transport = db.query(Transport).get(transport_id)
        transport.rating = round(avg_rating or 0.0, 1)

        db.commit()

class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True, index=True)
    id_from = Column(Integer, ForeignKey("cities.id"), nullable=False)
    id_to = Column(Integer, ForeignKey("cities.id"), nullable=False)

    from_city = relationship("Cities", back_populates="routes_from", foreign_keys=[id_from])
    to_city = relationship("Cities", back_populates="routes_to", foreign_keys=[id_to])
    transports = relationship("Transport", back_populates="route", lazy='dynamic', uselist=True)
    orders = relationship("Order", back_populates="route", lazy='dynamic', uselist=True)
    schedules = relationship("Schedule", back_populates="route", lazy='dynamic', uselist=True)
    transport_routes = relationship("TransportRoute", back_populates="route")


    __table_args__ = (
        UniqueConstraint("id_from", "id_to", name="uq_route_from_to"),
    )

class TransportRoute(Base): 
    __tablename__ = 'transport_routes'

    id = Column(Integer, primary_key=True, index=True)
    min_price = Column(Float)
    max_price = Column(Float)

    route_id = Column(Integer, ForeignKey('routes.id', ondelete="CASCADE"))
    transport_id = Column(Integer, ForeignKey('transports.id', ondelete="CASCADE"))
    route = relationship("Route", back_populates="transport_routes")
    transport = relationship("Transport", back_populates="transport_routes")

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, index=True)
    trip_start = Column(DateTime)
    trip_end = Column(DateTime)
    accepts_orders = Column(Boolean, default=True)

    id_transport = Column(Integer, ForeignKey('transports.id', ondelete="CASCADE"))
    transport = relationship("Transport", back_populates="schedules")
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"))
    route = relationship("Route", back_populates="schedules")


