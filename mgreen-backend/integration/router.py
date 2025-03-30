from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from core.dependencies import CommonDependencies
from utils.token import get_token
from utils.logger import logger
from .schemas import TelegramIntegrationCreate, TelegramIntegrationResponse
from .services import Integrations

router = APIRouter(
    prefix="/integration",
    tags=["Integration"],
    dependencies=[Depends(get_token)]
)

@router.post("/telegram", response_model=TelegramIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_telegram_integration(
    telegram_data: TelegramIntegrationCreate,
    commons: CommonDependencies = Depends()
):
    try:
        service = Integrations(commons.db)
        await service.kafka_producer.start()  
        result = await service.create_telegram_integration(telegram_data)
        return result
    except Exception as e:
        logger.error(f"Error in create_telegram_integration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/telegram/{telegram_id}", response_model=TelegramIntegrationResponse)
async def get_telegram_integration(
    telegram_id: int,
    commons: CommonDependencies = Depends()
):
    try:
        service = Integrations(commons.db)
        await service.kafka_producer.start() 
        result = await service.get_telegram_integration(telegram_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_telegram_integration: {str(e)}")
        raise HTTPException(status_code=404 if "not found" in str(e) else 500, detail=str(e))

@router.delete("/telegram/{telegram_id}", response_model=dict)
async def delete_telegram_integration(
    telegram_id: int,
    commons: CommonDependencies = Depends()
):
    try:
        service = Integrations(commons.db)
        await service.kafka_producer.start()  
        result = await service.delete_telegram_integration(telegram_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_telegram_integration: {str(e)}")
        raise HTTPException(status_code=404 if "not found" in str(e) else 500, detail=str(e))