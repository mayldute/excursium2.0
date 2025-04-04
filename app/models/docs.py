from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.enums import DocTypeEnum

class Docs(Base):
    __tablename__ = "docs"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(Enum(DocTypeEnum), nullable=False)
    file_path = Column(String, nullable=False)

    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    carrier = relationship("Carrier", back_populates="docs")

class ExtraService(Base):
    __tablename__ = "extra_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="extraservice", uselist=True)

    