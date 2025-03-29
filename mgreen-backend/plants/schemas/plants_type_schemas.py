from pydantic import BaseModel
from core.schemas import ReadBase

class PlantTypeBase(BaseModel):
    name: str
    description: str

    class Config:
        from_attributes = True

class PlantTypeRead(PlantTypeBase, ReadBase):
    pass

    class Config:
        from_attributes = True