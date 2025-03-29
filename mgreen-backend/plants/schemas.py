from pydantic import BaseModel
from core.schemas import ReadBase

class PlantBase(BaseModel):
    name: str

class PlantRead(PlantBase, ReadBase):
    pass