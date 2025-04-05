from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.models.enums import OrderStatusEnum, PassenderTypeEnum
from app.db.session import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(OrderStatusEnum), nullable=False)
    created_at = Column(DateTime, default=func.now())
    passenger_type = Column(Enum(PassenderTypeEnum), nullable=False)
    notification_sent = Column(Boolean, default=False)
    payment_status = Column(String(50), nullable=False)
    payment_method = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)

    comment = relationship("Comment", back_populates="order", uselist=False)
    extra_services = relationship("ExtraService", back_populates="order", uselist=True)
    id_client = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="orders")
    id_carrier = Column(Integer, ForeignKey("carriers.id"))
    carrier = relationship("Carrier", back_populates="orders")
    id_transport = Column(Integer, ForeignKey("transports.id"))
    transport = relationship("Transport", back_populates="orders")
    id_route = Column(Integer, ForeignKey("routes.id"))
    route = relationship("Route", back_populates="orders")
    
class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    rating = Column(Integer, nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="comments")
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="comment", uselist=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    carrier = relationship("Carrier", back_populates="comments")
    


