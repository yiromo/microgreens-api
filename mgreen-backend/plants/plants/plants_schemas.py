from pydantic import BaseModel, Field, field_validator
from core.schemas import ReadBase
from typing import Optional, List
from uuid import UUID
from plants.plants_type.plants_type_schemas import PlantTypeRead as PlantTypeReadSchema

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

class PlantListResponse(BaseModel):
    items: List[PlantRead] = Field(..., description="List of plants")
    page_size: int = Field(..., description="Number of items per page")
    page_count: int = Field(..., description="Total number of pages based on page_size")

    class Config:
        from_attributes = True