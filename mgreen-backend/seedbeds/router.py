from fastapi import APIRouter, HTTPException, Path, Query, Response, Depends
from .schemas import *
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import CommonDependencies
from utils.token import get_token
from fastapi import status
from .services import SeedbedsService
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/seedbeds",
    dependencies=[Depends(get_token)],
    tags=["Seedbeds"]
)


@router.get("/all", response_model=GetAllSeedbedsResponse)
async def get_all_journals(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    commons: CommonDependencies = Depends()
):
    db: AsyncSession = commons.db
    seedbeds_service = SeedbedsService(db)

    try:
        journals, total_count = await seedbeds_service.get_all_seedbeds(page, page_size)

        page_count = (total_count + page_size - 1) // page_size
        
        return {
            "seedbeds": journals,
            "page": page,
            "page_size": page_size,
            "page_count": page_count
        }
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при получении журналов: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении журналов: {str(e)}"
        )
    
@router.get("/by-id/{id}", response_model=Optional[SeedbedResponseFull])
async def get_seedbed(id: int, commons: CommonDependencies = Depends()):
    db: AsyncSession = commons.db
    seedbeds_service = SeedbedsService(db)
    return await seedbeds_service.get_seedbed_by_id(id)


@router.post("/add", response_model=AddSeedbedResponse)
async def add_new_record(
    seedbed: SeedbedBase,
    commons: CommonDependencies = Depends()
):
    db: AsyncSession = commons.db
    seedbeds_service = SeedbedsService(db)

    try:
        new_journal = await seedbeds_service.add_new_record(seedbed.dict())
        return {
            "message": "Запись успешно добавлена",
            "seedbed": new_journal
        }
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при добавлении записи: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении записи: {str(e)}"
        )


@router.delete("/delete/{id}", response_model=DeleteSeedbedResponse)
async def delete_journal(
    id: int = Path(..., ge=1, description="ID грядки"),
    commons: CommonDependencies = Depends()
):
    db: AsyncSession = commons.db
    seedbeds_service = SeedbedsService(db)

    try:
        await seedbeds_service.delete_seedbed(id)


        return {
            "message": "Запись успешно удалена"
        }
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при удалении записи: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении записи: {str(e)}"
        )

