from fastapi import APIRouter, Response, Depends, HTTPException, status
from .plants_type_schemas import PlantTypeBase, PlantTypeRead
from .plants_type_service import PlantsTypeService
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import CommonDependencies
from core.dependencies import get_db
from utils.token import get_token

router = APIRouter(
    prefix="/plant-type",
    tags=["Plant Type"],
    dependencies=[Depends(get_token)]
)

@router.get("/all/", response_model=List[PlantTypeRead])
async def get_all(
    page: int = 1,
    limit: int = 10,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsTypeService(db)
    plant_types = await service.get_all(page=page, limit=limit)
    return plant_types

@router.get("/{id}", response_model=PlantTypeRead)
async def get_by_id(
    id: str,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsTypeService(db)
    plant_type = await service.get_by_id(id)
    if not plant_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant type not found"
        )
    return plant_type

@router.post("/", response_model=PlantTypeRead, status_code=status.HTTP_201_CREATED)
async def create_plant_type(
    plant_type: PlantTypeBase,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsTypeService(db)
    created_plant_type = await service.create(plant_type)
    return created_plant_type

@router.put("/{id}", response_model=PlantTypeRead)
async def update_plant_type(
    id: str,
    plant_type: PlantTypeBase,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsTypeService(db)
    updated_plant_type = await service.update(id, plant_type)
    if not updated_plant_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant type not found"
        )
    return updated_plant_type

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant_type(
    id: str,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsTypeService(db)
    deleted = await service.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant type not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)