from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.enums import ClientTypeEnum, LegalTypeEnum
from app.models.order import Comment
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    middle_name = Column(String(255), nullable=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String(16), unique=True, index=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_subscribed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    photo = Column(String, nullable=True)
    hashed_password = Column(String(255), nullable=False)

    client = relationship("Client", back_populates="user", uselist=False, cascade="all, delete-orphan")
    carrier = relationship("Carrier", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_token = relationship("RefreshToken", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_type = Column(Enum(ClientTypeEnum), nullable=False)
    legal_type = Column(Enum(LegalTypeEnum), nullable=True)
    company_name = Column(String(255), nullable=True)
    inn = Column(String(12), nullable=True, index=True, unique=True)
    kpp = Column(String(9), nullable=True, unique=True)
    ogrn = Column(String(13), nullable=True, unique=True)
    current_account = Column(String(20), nullable=True, unique=True)
    corresp_account = Column(String(20), nullable=True, unique=True)
    bik = Column(String(9), nullable=True, unique=True)
    oktmo = Column(String(11), nullable=True, unique=True)
    address = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="client", uselist=False)
    comments = relationship("Comment", back_populates="client", lazy='dynamic', uselist=True)
    orders = relationship("Order", back_populates="client", lazy='dynamic', uselist=True)

class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    carrier_type = Column(Enum(LegalTypeEnum), nullable=True)
    custom_type = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=False)
    inn = Column(String(12), nullable=True, index=True, unique=True)
    kpp = Column(String(9), nullable=True, unique=True)
    ogrn = Column(String(13), nullable=True, unique=True)
    current_account = Column(String(20), nullable=True, unique=True)
    corresp_account = Column(String(20), nullable=True, unique=True)
    bik = Column(String(9), nullable=True, unique=True)
    oktmo = Column(String(11), nullable=True, unique=True)
    address = Column(String(255), nullable=True)
    rating = Column(Float, default=0.0)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="carrier", uselist=False)
    docs = relationship("Docs", back_populates="carrier", lazy='dynamic', uselist=True)
    transports = relationship("Transport", back_populates="carrier", lazy='dynamic', uselist=True)
    comments = relationship("Comment", back_populates="carrier", lazy='dynamic', uselist=True)
    orders = relationship("Order", back_populates="carrier", lazy='dynamic', uselist=True)

    @staticmethod
    def update_carrier_rating(db, carrier_id: int):
        avg_rating = db.query(func.avg(Comment.rating))\
            .filter(Comment.carrier_id == carrier_id)\
            .scalar()

        carrier = db.query(Carrier).get(carrier_id)
        carrier.rating = round(avg_rating or 0.0, 1)

        db.commit()