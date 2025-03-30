from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, String, Integer, BigInteger, DateTime, ForeignKey, Float
from database import Base  


class Records(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, doc="ID записи")

    soilId: Mapped[int] = mapped_column(
        ForeignKey("seedbeds.id", ondelete="CASCADE"),
        nullable=False, doc="ID почвы, к которой относится запись"
    )
    
    photo_link: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Ссылка на фото")
    
    water_temperature: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Температура воды"
    )

    air_temperature: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Температура воздуха"
    )

    air_humidity: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Влажность воздуха"
    )
    
    light_level: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Уровень света"
    )
    height_plant: Mapped[float] = mapped_column(
        Float, nullable=True, doc="Высота растения"
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