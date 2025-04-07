from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.models.enums import ClientTypeEnum, LegalTypeEnum
from app.models.order import Comment
from app.db.session import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    middle_name = Column(String(255), nullable=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String(15), unique=True, index=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_subscribed = Column(Boolean, default=False)
    date_joined = Column(DateTime, default=func.now())
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
    inn = Column(String(12), nullable=True, index=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(13), nullable=True)
    current_account = Column(String(20), nullable=True)
    corresp_account = Column(String(20), nullable=True)
    bik = Column(String(9), nullable=True)
    oktmo = Column(String(11), nullable=True)
    address = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="client", uselist=False)
    comments = relationship("Comment", back_populates="client", lazy='dynamic', uselist=True)
    orders = relationship("Order", back_populates="client", lazy='dynamic', uselist=True)

class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    carrier_type = Column(Enum(LegalTypeEnum), nullable=True)
    company_name = Column(String(255), nullable=False)
    inn = Column(String(12), nullable=True, index=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(13), nullable=True)
    current_account = Column(String(20), nullable=True)
    corresp_account = Column(String(20), nullable=True)
    bik = Column(String(9), nullable=True)
    oktmo = Column(String(11), nullable=True)
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