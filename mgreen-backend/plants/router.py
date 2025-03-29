from fastapi import APIRouter, Response, Depends
from .schemas import *
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import CommonDependencies
from utils.token import get_token

router = APIRouter(
    prefix="/microgreen",
    tags=["Microgreen"],
    dependencies=[Depends(get_token)]
)

@router.post("/plant")
async def create_plant(commons: CommonDependencies = Depends()):
    db = commons.db
    auth_service = commons.auth_service
    token = commons.token
    pass

@router.post("/plant/image")
async def create_plant_by_image(commons: CommonDependencies = Depends()):
    db = commons.db
    auth_service = commons.auth_service
    token = commons.token
    pass
