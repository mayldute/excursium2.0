from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    func,
    ForeignKey,
    UniqueConstraint,
    Enum
)

from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ScheduleReasonEnum


class Transport(Base):
    __tablename__ = 'transports'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    n_seat: Mapped[int] = mapped_column(Integer)
    photo: Mapped[str | None] = mapped_column(String, nullable=True)
    luggage: Mapped[bool] = mapped_column(Boolean, default=False)
    wifi: Mapped[bool] = mapped_column(Boolean, default=False)
    tv: Mapped[bool] = mapped_column(Boolean, default=False)
    air_conditioning: Mapped[bool] = mapped_column(Boolean, default=False)
    toilet: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)

    carrier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("carriers.id", ondelete="CASCADE")
    )
    carrier: Mapped["Carrier"] = relationship(back_populates="transports")
    orders: Mapped[list["Order"]] = relationship(
        back_populates="transport", lazy='dynamic', uselist=True
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="transport", uselist=True
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="transport", lazy='dynamic', uselist=True
    )
    transport_routes: Mapped[list["TransportRoute"]] = relationship(
        back_populates="transport", cascade="all, delete-orphan"
    )

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_from: Mapped[int] = mapped_column(
        Integer, ForeignKey("cities.id"), nullable=False
    )
    id_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("cities.id"), nullable=False
    )
    from_city: Mapped["City"] = relationship(
        back_populates="routes_from", foreign_keys=[id_from]
    )
    to_city: Mapped["City"] = relationship(
        back_populates="routes_to", foreign_keys=[id_to]
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="route", lazy='dynamic', uselist=True
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="route", lazy='dynamic', uselist=True
    )
    transport_routes: Mapped[list["TransportRoute"]] = relationship(
        back_populates="route", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("id_from", "id_to", name="uq_route_from_to"),
    )


class TransportRoute(Base):
    __tablename__ = 'transport_routes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    min_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)

    route_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    transport_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transports.id", ondelete="CASCADE"), nullable=False
    )
    route: Mapped["Route"] = relationship(
        "Route", back_populates="transport_routes"
    )
    transport: Mapped["Transport"] = relationship(
        "Transport", back_populates="transport_routes"
    )


class Schedule(Base):
    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    reason : Mapped[ScheduleReasonEnum] = mapped_column(
        Enum(ScheduleReasonEnum),
        nullable=False,
        default=ScheduleReasonEnum.TECHNICAL
    )

    id_transport: Mapped[int] = mapped_column(
        Integer, ForeignKey('transports.id', ondelete="CASCADE")
    )
    transport: Mapped["Transport"] = relationship(back_populates="schedules")
    route_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=True
    )
    route: Mapped["Route"] = relationship(back_populates="schedules")
