from fastapi import APIRouter, HTTPException, Query, Response, Depends
from .schemas import *
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import CommonDependencies
from utils.token import get_token
from fastapi import status
from .services import JournalService
from sqlalchemy.exc import IntegrityError
from .schemas import JournalCreate

router = APIRouter(
    prefix="/journal",
    dependencies=[Depends(get_token)],
    tags=["Journal"]
)


@router.get("/all")
async def get_all_journals(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    commons: CommonDependencies = Depends()
):
    db: AsyncSession = commons.db
    journal_service = JournalService(db)

    try:
        journals, total_count = await journal_service.get_all_journals(page, page_size)

        page_count = (total_count + page_size - 1) // page_size
        
        return {
            "journals": journals,
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


@router.post("/add")
async def add_new_record(
    journal: JournalCreate,
    commons: CommonDependencies = Depends()
):
    db: AsyncSession = commons.db
    journal_service = JournalService(db)

    try:
        new_journal = await journal_service.add_new_record(journal.dict())
        return {
            "message": "Запись успешно добавлена",
            "journal": new_journal
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



