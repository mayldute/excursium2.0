from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.enums import ClientTypeEnum, LegalTypeEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    middle_name = Column(String(255), nullable=True)
    email = Column(String, unique=True)
    phone_number = Column(String(15), unique=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_subscribed = Column(Boolean, default=False)
    date_joined = Column(DateTime, default=func.now)
    photo = Column(String, nullable=True)
    hashed_password = Column(String(255), nullable=False)

    client = relationship("Client", back_populates="user", uselist=False)
    carrier = relationship("Carrier", back_populates="user", uselist=False)

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_type = Column(Enum(ClientTypeEnum), nullable=False)
    legal_type = Column(Enum(LegalTypeEnum), nullable=True)
    company_name = Column(String(255), nullable=True)
    inn = Column(String(12), nullable=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(13), nullable=True)
    current_account = Column(String(20), nullable=True)
    corresp_account = Column(String(20), nullable=True)
    bik = Column(String(9), nullable=True)
    oktmo = Column(String(11), nullable=True)
    address = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="client", uselist=False)
    comment = relationship("Comment", back_populates="comment", uselist=True)
    order = relationship("Order", back_populates="client", uselist=False)

class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    carrier_type = Column(Enum(LegalTypeEnum), nullable=True)
    company_name = Column(String(255), nullable=False)
    inn = Column(String(12), nullable=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(13), nullable=True)
    current_account = Column(String(20), nullable=True)
    corresp_account = Column(String(20), nullable=True)
    bik = Column(String(9), nullable=True)
    oktmo = Column(String(11), nullable=True)
    address = Column(String(255), nullable=True)
    rating = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="carrier", uselist=False)
    docs = relationship("Docs", back_populates="carrier", uselist=True)
    transport = relationship("Transport", back_populates="carrier", uselist=True)
    comment = relationship("Comment", back_populates="carrier", uselist=False)
    order = relationship("Order", back_populates="carrier", uselist=False)