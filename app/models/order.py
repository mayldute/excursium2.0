from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.models.enums import OrderStatusEnum, PassenderTypeEnum, PaymentMethodEnum, PaymentStatusEnum
from app.db.session import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(OrderStatusEnum), nullable=False)
    created_at = Column(DateTime, default=func.now())
    passenger_type = Column(Enum(PassenderTypeEnum), nullable=False)
    notification_sent = Column(Boolean, default=False)
    payment_status = Column(Enum(PaymentStatusEnum), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    price = Column(Integer, nullable=False)

    comment = relationship("Comment", back_populates="order", uselist=False)
    extra_services = relationship("ExtraService", back_populates="order", lazy='dynamic', uselist=True)
    id_client = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship("Client", back_populates="orders")
    id_carrier = Column(Integer, ForeignKey("carriers.id", ondelete="CASCADE"))
    carrier = relationship("Carrier", back_populates="orders")
    id_transport = Column(Integer, ForeignKey("transports.id", ondelete="CASCADE"))
    transport = relationship("Transport", back_populates="orders")
    id_route = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"))
    route = relationship("Route", back_populates="orders")
    history = relationship("OrderHistory", back_populates="order", cascade="all, delete-orphan", lazy='dynamic')

class OrderHistory(Base):
    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum(OrderStatusEnum), nullable=True)
    new_status = Column(Enum(OrderStatusEnum), nullable=False)
    changed_at = Column(DateTime, default=func.now())
    changed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    comment = Column(String, nullable=True)

    order = relationship("Order", back_populates="history")
    changed_by = relationship("User")
    
class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    rating = Column(Integer, nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship("Client", back_populates="comments")
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    order = relationship("Order", back_populates="comment", uselist=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id", ondelete="CASCADE"))
    carrier = relationship("Carrier", back_populates="comments")
    transport_id = Column(Integer, ForeignKey("transports.id", ondelete="CASCADE"))
    transport = relationship("Transport", back_populates="comments")
    


