from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.transport import Route


class City(Base):
    __tablename__ = 'cities'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)

    routes_from: Mapped[list["Route"]] = relationship(
        "Route", back_populates="from_city", foreign_keys=[Route.id_from]
    )
    routes_to: Mapped[list["Route"]] = relationship(
        "Route", back_populates="to_city", foreign_keys=[Route.id_to]
    )
