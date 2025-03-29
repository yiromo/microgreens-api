from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, String, Integer, BigInteger, DateTime
from database import Base   

class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    soil_number: Mapped[int] = mapped_column(Integer, nullable=False)
    water_temperature: Mapped[float] = mapped_column(BigInteger, nullable=False)
    air_temperature: Mapped[float] = mapped_column(BigInteger, nullable=False)
    air_humidity: Mapped[float] = mapped_column(BigInteger, nullable=False)
    light_level: Mapped[float] = mapped_column(BigInteger, nullable=False)

    plant_type: Mapped[str] = mapped_column(String(50), nullable=False)
    date_planted: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=False
    )
    
    type_of_soil: Mapped[str] = mapped_column(String(50), nullable=False)

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





