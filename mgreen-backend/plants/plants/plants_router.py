from fastapi import APIRouter, Response, Depends, HTTPException, status, UploadFile, File
from .plants_schemas import PlantBase, PlantRead, PlantListResponse
from .plants_service import PlantsService
from typing import List
from core.dependencies import CommonDependencies
from utils.token import get_token
from utils.logger import logger

router = APIRouter(
    prefix="/plant",
    tags=["Plant"],
    dependencies=[Depends(get_token)]
)

@router.get("/all", response_model=PlantListResponse)
async def get_all_plants(
    page: int = 1,
    page_size: int = 10,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsService(db)
    plant_list = await service.get_all(page=page, page_size=page_size)
    return plant_list

@router.get("/{id}", response_model=PlantRead)
async def get_plant(
    id: str,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsService(db)
    plant = await service.get_by_id(id)
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    return plant

@router.post("/", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant: PlantBase,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsService(db)
    created_plant = await service.create(plant)
    return created_plant

@router.put("/{id}", response_model=PlantRead)
async def update_plant(
    id: str,
    plant: PlantBase,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsService(db)
    updated_plant = await service.update(id, plant)
    if not updated_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    return updated_plant

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    id: str,
    commons: CommonDependencies = Depends()
):
    db = commons.db
    service = PlantsService(db)
    deleted = await service.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/by-image", response_model=List[PlantRead])
async def create_plant_by_image(image: UploadFile = File(...), commons: CommonDependencies = Depends()):
    db = commons.db
    auth_service = commons.auth_service
    token = commons.token
    service = PlantsService(db)
    try:
        logger.info(f"Received image upload: {image.filename}, content-type: {image.content_type}")
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        await image.seek(0)
        test_bytes = await image.read(1024)
        logger.info(f"Successfully read {len(test_bytes)} bytes from the image")
        
        await image.seek(0)
        
        return await service.create_from_image_analysis(image)
        
    except Exception as e:
        logger.error(f"Error in create_plant_by_image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))