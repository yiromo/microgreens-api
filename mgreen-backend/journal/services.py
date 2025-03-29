import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import get_db
from typing import Optional, Tuple, List
from .models import Journal


class JournalService():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_journals(
        self, 
        page: int = 1, 
        page_size: int = 10
    ) -> List[Journal]:
        try:
            offset = (page - 1) * page_size
            
            query = select(Journal).offset(offset).limit(page_size)
            result = await self.db.execute(query)
            journals = result.scalars().all()
    
            count_query = select(func.count()).select_from(Journal)
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            return journals, total_count
        
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении журналов: {str(e)}")
            raise e


    async def add_new_record(
        self,
        kwargs: dict
    ):
        try:
            new_journal = Journal(**kwargs)
            self.db.add(new_journal)
            await self.db.commit()
            await self.db.refresh(new_journal)
            return new_journal
        except IntegrityError as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            raise e
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            raise e