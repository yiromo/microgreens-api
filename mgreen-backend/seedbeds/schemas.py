from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import uuid
from plants.plants.plants_schemas import PlantRead

class SeedbedBase(BaseModel):
    soil_number: int = Field(..., description="Номер почвы")
    plant_id: uuid.UUID = Field(..., description="ID растения")
    date_planted: datetime = Field(..., description="Дата посадки")
    type_of_soil: str = Field(..., description="Тип почвы")
    date_harvested: datetime = Field(..., description="Дата сбора урожая")

class DeleteSeedbedResponse(BaseModel):
    message: str


class SeedbedResponse(SeedbedBase):
    id: int = Field(..., description="ID грядки")
    plant_name: str = Field(..., description="Название растения")
    
    class Config:
        from_attributes = True

class SeedbedResponseFull(SeedbedResponse):
    plant: PlantRead
    
    @field_validator("plant_id", mode="before")
    def coerce_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True

class AddSeedbedResponse(BaseModel):
    message: str
    seedbed: SeedbedResponse

class GetAllSeedbedsResponse(BaseModel):
    seedbeds: List[SeedbedResponse]
    page: int
    page_size: int
    page_count: int