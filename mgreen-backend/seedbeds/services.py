import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import get_db
from typing import Optional, Tuple, List
from .models import Seedbeds
from fastapi import HTTPException
from plants.models import Plants, PlantsType
from .schemas import SeedbedResponseFull
from datetime import datetime

class SeedbedsService():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_seedbeds(
        self, 
        page: int = 1, 
        page_size: int = 10
    ) -> List[Seedbeds]:
        try:
            offset = (page - 1) * page_size
            
            query = (
                select(Seedbeds, Plants.name.label("plant_name"))
                .join(Plants, Seedbeds.plant_id == Plants.id)
                .offset(offset)
                .limit(page_size)
            )
            
            result = await self.db.execute(query)
            rows = result.all()
            
            seedbeds = []
            for row in rows:
                seedbed_dict = row[0].__dict__
                seedbed_dict.pop('_sa_instance_state', None) 
                seedbed_dict['plant_name'] = row[1] 
                seedbeds.append(seedbed_dict)
            
            count_query = select(func.count()).select_from(Seedbeds)
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            return seedbeds, total_count
        
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении записей о грядках: {str(e)}")
            raise e

    async def get_seedbed_by_id(self, id: int) -> Optional[SeedbedResponseFull]:
        try:
            query = (
                select(Seedbeds, Plants, PlantsType)
                .join(Plants, Seedbeds.plant_id == Plants.id)
                .join(PlantsType, Plants.plant_type_id == PlantsType.id)
                .where(Seedbeds.id == id)
            )
            result = await self.db.execute(query)
            row = result.first()

            if not row:
                return None

            seedbed = row[0]  
            plant = row[1]    
            plant_type = row[2]  

            seedbed_dict = seedbed.__dict__.copy()
            seedbed_dict.pop('_sa_instance_state', None)
            seedbed_dict['plant_name'] = plant.name  

            plant_dict = plant.__dict__.copy()
            plant_dict.pop('_sa_instance_state', None)
            plant_dict['plant_type'] = plant_type.__dict__.copy()
            plant_dict['plant_type'].pop('_sa_instance_state', None)

            seedbed_dict['plant'] = plant_dict

            return seedbed_dict

        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении грядки по ID: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    async def update_seedbed_date_harvested(self, id: int, date_harvested: datetime) -> Optional[dict]:
        try:
            query = select(Seedbeds).where(Seedbeds.id == id)
            result = await self.db.execute(query)
            seedbed = result.scalars().first()

            if not seedbed:
                return None  

            seedbed.date_harvested = date_harvested
            await self.db.commit()
            await self.db.refresh(seedbed)

            return seedbed.__dict__.copy()

        except SQLAlchemyError as e:
            logging.error(f"Ошибка при обновлении даты сбора урожая: {str(e)}")
            raise e

    async def add_new_record(
        self,
        kwargs: dict
    ):
        try:
            new_journal = Seedbeds(**kwargs)
            self.db.add(new_journal)
            await self.db.commit()
            await self.db.refresh(new_journal)
            
            plant_query = select(Plants.name).where(Plants.id == new_journal.plant_id)
            plant_result = await self.db.execute(plant_query)
            plant_name = plant_result.scalar()
            
            response_data = new_journal.__dict__.copy()
            response_data.pop('_sa_instance_state', None)
            response_data['plant_name'] = plant_name
            
            return response_data
        except IntegrityError as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            raise e
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            raise e
    
    async def delete_seedbed(
        self,
        seedbed_id: int
    ) -> Optional[Seedbeds]:
        try:
            query = select(Seedbeds).where(Seedbeds.id == seedbed_id)
            result = await self.db.execute(query)
            seedbed = result.scalars().first()
            
            if seedbed:
                await self.db.delete(seedbed)
                await self.db.commit()
                return seedbed
            else:
                return None
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при удалении записи: {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Ошибка при удалении записи: {str(e)}")
            raise e
        