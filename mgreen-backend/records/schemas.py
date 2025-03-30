from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import uuid
import base64
import re


class RecordsBase(BaseModel):
    water_temperature: float = Field(..., description="Температура воды")
    air_temperature: float = Field(..., description="Температура воздуха")
    air_humidity: float = Field(..., description="Влажность воздуха")
    light_level: float = Field(..., description="Уровень света")
    height_plant: float = Field(None, description="Высота растения")
    photo_link: Optional[str] = Field(None, description="Фотография в формате base64")
    
class RecordsResponse(RecordsBase):
    id: int = Field(..., description="ID записи")
    created_at: datetime = Field(..., description="Дата создания записи")
    soilId: int = Field(..., description="ID почвы")
    
    class Config:
        from_attributes = True

class AddRecordResponse(BaseModel):
    message: str
    record: RecordsResponse

class GetAllRecordsResponse(BaseModel):
    records: List[RecordsResponse]
    page: int
    page_size: int
    page_count: int