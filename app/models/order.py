from sqlalchemy import Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from app.models.enums import (
    OrderStatusEnum, 
    PassengerTypeEnum, 
    PaymentMethodEnum, 
    PaymentStatusEnum
)

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[OrderStatusEnum] = mapped_column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.NEW)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    passenger_type: Mapped[PassengerTypeEnum] = mapped_column(Enum(PassengerTypeEnum), nullable=False)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(Enum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.PENDING)
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(Enum(PaymentMethodEnum), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)

    comment: Mapped["Comment"] = relationship("Comment", back_populates="order", uselist=False)
    extra_services: Mapped[list["ExtraService"]] = relationship("ExtraService", back_populates="order", lazy='dynamic', uselist=True)
    id_client: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client: Mapped["Client"] = relationship("Client", back_populates="orders")
    id_carrier: Mapped[int] = mapped_column(Integer, ForeignKey("carriers.id", ondelete="CASCADE"))
    carrier: Mapped["Carrier"] = relationship("Carrier", back_populates="orders")
    id_transport: Mapped[int] = mapped_column(Integer, ForeignKey("transports.id", ondelete="CASCADE"))
    transport: Mapped["Transport"] = relationship("Transport", back_populates="orders")
    id_route: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id", ondelete="CASCADE"))
    route: Mapped["Route"] = relationship("Route", back_populates="orders")
    history: Mapped[list["OrderHistory"]] = relationship("OrderHistory", back_populates="order", cascade="all, delete-orphan", lazy='dynamic')

class OrderHistory(Base):
    __tablename__ = "order_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    old_status: Mapped[OrderStatusEnum | None] = mapped_column(Enum(OrderStatusEnum), nullable=True)
    new_status: Mapped[OrderStatusEnum] = mapped_column(Enum(OrderStatusEnum), nullable=False)
    changed_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    changed_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="history")
    changed_by: Mapped["User"] = relationship("User")

class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    answer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client: Mapped["Client"] = relationship("Client", back_populates="comments")
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    order: Mapped["Order"] = relationship("Order", back_populates="comment", uselist=False)
    carrier_id: Mapped[int] = mapped_column(Integer, ForeignKey("carriers.id", ondelete="CASCADE"))
    carrier: Mapped["Carrier"] = relationship("Carrier", back_populates="comments")
    transport_id: Mapped[int] = mapped_column(Integer, ForeignKey("transports.id", ondelete="CASCADE"))
    transport: Mapped["Transport"] = relationship("Transport", back_populates="comments")


