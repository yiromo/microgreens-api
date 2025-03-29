from pydantic import BaseModel, Field, field_validator
from core.schemas import ReadBase
from typing import Optional
from uuid import UUID
from plants.schemas.plants_type_schemas import PlantTypeRead as PlantTypeReadSchema  

class PlantBase(BaseModel):
    name: str
    typical_days_to_harvest: int
    description: str
    plant_type_id: str 

    class Config:
        from_attributes = True

class PlantRead(PlantBase, ReadBase):
    plant_type: PlantTypeReadSchema = Field(..., description="Details of the associated plant type")

    @field_validator("id", "plant_type_id", mode="before")
    def coerce_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True