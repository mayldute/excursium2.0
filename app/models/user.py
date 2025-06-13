from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    func,
    Enum,
    Float,
    ForeignKey
)

from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ClientTypeEnum, LegalTypeEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, nullable=True
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_subscribed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_oauth_user: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    photo: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)

    client: Mapped["Client"] = relationship(
        "Client",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    carrier: Mapped["Carrier"] = relationship(
        "Carrier",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    refresh_token: Mapped["RefreshToken"] = relationship(
        "RefreshToken",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    change_email: Mapped["ChangeEmail"] = relationship(
        "ChangeEmail",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_type: Mapped[ClientTypeEnum] = mapped_column(
        Enum(ClientTypeEnum), nullable=False
    )
    legal_type: Mapped[LegalTypeEnum | None] = mapped_column(
        Enum(LegalTypeEnum), nullable=True
    )
    custom_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inn: Mapped[str | None] = mapped_column(
        String(12), nullable=True, index=True, unique=True
    )
    kpp: Mapped[str | None] = mapped_column(
        String(9), nullable=True, unique=True
    )
    ogrn: Mapped[str | None] = mapped_column(
        String(13), nullable=True, unique=True
    )
    current_account: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True
    )
    corresp_account: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True
    )
    bik: Mapped[str | None] = mapped_column(
        String(9), nullable=True, unique=True
    )
    oktmo: Mapped[str | None] = mapped_column(
        String(11), nullable=True, unique=True
    )
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="client", uselist=False
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="client", lazy='dynamic', uselist=True
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="client", lazy='dynamic', uselist=True
    )


class Carrier(Base):
    __tablename__ = "carriers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    legal_type: Mapped[LegalTypeEnum | None] = mapped_column(
        Enum(LegalTypeEnum), nullable=True
    )
    custom_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str | None] = mapped_column(
        String(12), nullable=True, index=True, unique=True
    )
    kpp: Mapped[str | None] = mapped_column(
        String(9), nullable=True, unique=True
    )
    ogrn: Mapped[str | None] = mapped_column(
        String(13), nullable=True, unique=True
    )
    current_account: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True
    )
    corresp_account: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True
    )
    bik: Mapped[str | None] = mapped_column(
        String(9), nullable=True, unique=True
    )
    oktmo: Mapped[str | None] = mapped_column(
        String(11), nullable=True, unique=True
    )
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_business_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="carrier", uselist=False
    )
    docs: Mapped[list["Docs"]] = relationship(
        "Docs", back_populates="carrier", lazy='dynamic', uselist=True
    )
    transports: Mapped[list["Transport"]] = relationship(
        "Transport", back_populates="carrier", lazy='dynamic', uselist=True
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="carrier", lazy='dynamic', uselist=True
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="carrier", lazy='dynamic', uselist=True
    )

    @staticmethod
    def update_carrier_rating(db, carrier_id: int):
        avg_rating = db.query(func.avg(Comment.rating))\
            .filter(Comment.carrier_id == carrier_id)\
            .scalar()

        carrier = db.query(Carrier).get(carrier_id)
        carrier.rating = round(avg_rating or 0.0, 1)

        db.commit()


class ChangeEmail(Base):
    __tablename__ = "change_email"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    new_email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    token: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="change_email", uselist=False
    )
