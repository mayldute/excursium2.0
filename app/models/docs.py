from sqlalchemy import Integer, String, Text, Enum, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DocTypeEnum, DocStatusEnum


class Docs(Base):
    __tablename__ = "docs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    doc_type: Mapped[DocTypeEnum] = mapped_column(
        Enum(DocTypeEnum), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DocStatusEnum] = mapped_column(
        Enum(DocStatusEnum), nullable=False, default=DocStatusEnum.PENDING
    )

    carrier_id: Mapped[int] = mapped_column(
        ForeignKey("carriers.id", ondelete="CASCADE")
    )
    carrier: Mapped["Carrier"] = relationship("Carrier", back_populates="docs")


class ExtraService(Base):
    __tablename__ = "extra_services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE")
    )
    order: Mapped["Order"] = relationship(
        "Order", back_populates="extra_services"
    )
