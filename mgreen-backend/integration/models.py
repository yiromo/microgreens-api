from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, String, Integer, BigInteger, DateTime, ForeignKey
from database import Base  
from sqlalchemy.dialects.postgresql import UUID 
import uuid


class TelegramIntegration(Base):
    __tablename__ = "telegram_integration"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  
        index=True,
    )
    
    telegram_id : Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        doc="TelegramId пользователя, которому принадлежит интеграция")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(),
        doc="Timestamp when the registration record was created."
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.now(),
        doc="Timestamp when the registration record was last updated."
    )
    