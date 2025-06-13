from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Newsletter(Base):
    __tablename__ = 'newsletters'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    header: Mapped[str] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
