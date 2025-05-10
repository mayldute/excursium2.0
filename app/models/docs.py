from sqlalchemy import Column, Integer, String, Text, Enum, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import DocTypeEnum

class Docs(Base):
    __tablename__ = "docs"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(Enum(DocTypeEnum), nullable=False)
    file_path = Column(String, nullable=False)

    carrier_id = Column(Integer, ForeignKey("carriers.id", ondelete="CASCADE"))
    carrier = relationship("Carrier", back_populates="docs")

class ExtraService(Base):
    __tablename__ = "extra_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    order = relationship("Order", back_populates="extra_services")

    