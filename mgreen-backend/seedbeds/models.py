from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, String, Integer, BigInteger, DateTime, ForeignKey
from database import Base   
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Seedbeds(Base):
    __tablename__ = "seedbeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    soil_number: Mapped[int] = mapped_column(Integer, nullable=False)

    plant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plants.id"), nullable=False
    )

    type_of_soil: Mapped[str] = mapped_column(String(50), nullable=False)

    date_planted: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False
    )
    date_harvested: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False
    )
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
