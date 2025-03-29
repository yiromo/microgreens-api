from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from plants.models import PlantsType
from .plants_type_schemas import PlantTypeRead, PlantTypeBase
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PlantsTypeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, page: int = 1, limit: int = 10) -> List[PlantTypeRead]:
        offset = (page - 1) * limit
        query = (
            select(PlantsType)
            .options(selectinload(PlantsType.plants))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        plant_types = result.scalars().all()
        return [PlantTypeRead.model_validate(pt) for pt in plant_types]

    async def get_by_id(self, id: str) -> Optional[PlantTypeRead]:
        query = (
            select(PlantsType)
            .where(PlantsType.id == UUID(id))
            .options(selectinload(PlantsType.plants))
        )
        result = await self.db.execute(query)
        plant_type = result.scalar_one_or_none()
        if plant_type:
            return PlantTypeRead.model_validate(plant_type)
        return None

    async def create(self, plant_type_data: PlantTypeBase) -> PlantTypeRead:
        new_plant_type = PlantsType(
            name=plant_type_data.name,
            description=plant_type_data.description,
        )
        self.db.add(new_plant_type)
        await self.db.commit()
        await self.db.refresh(new_plant_type)
        return PlantTypeRead.model_validate(new_plant_type)

    async def update(self, id: str, plant_type_data: PlantTypeBase) -> Optional[PlantTypeRead]:
        query = (
            update(PlantsType)
            .where(PlantsType.id == UUID(id))
            .values(
                name=plant_type_data.name,
                description=plant_type_data.description,
                updated_at=datetime.now()
            )
            .returning(PlantsType)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        plant_type = result.scalar_one_or_none()
        if plant_type:
            return PlantTypeRead.model_validate(plant_type)
        return None

    async def delete(self, id: str) -> bool:
        query = delete(PlantsType).where(PlantsType.id == UUID(id))
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0