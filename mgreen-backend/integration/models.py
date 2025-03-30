from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, String, Integer, BigInteger, DateTime, ForeignKey
from database import Base  


class TelegramIntegration(Base):
    __table__ = "telegram_integration"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, doc="ID записи")
    
    used_id : Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        doc="ID пользователя, которому принадлежит интеграция")
    
    