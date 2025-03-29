from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class JournalCreate(BaseModel):
    soil_number: int = Field(..., description="Номер почвы")
    water_temperature: float = Field(..., description="Температура воды")
    air_temperature: float = Field(..., description="Температура воздуха")
    air_humidity: float = Field(..., description="Влажность воздуха")
    light_level: float = Field(..., description="Уровень света")
    plant_type: str = Field(..., description="Тип растения")
    date_planted: datetime = Field(..., description="Дата посадки")
    type_of_soil: str = Field(..., description="Тип почвы")
    date_harvested: datetime = Field(..., description="Дата сбора урожая")

