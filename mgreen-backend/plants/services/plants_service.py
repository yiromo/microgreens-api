from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from plants.models import Plants
from plants.schemas.plants_schemas import PlantBase, PlantRead
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PlantsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, page: int = 1, limit: int = 10) -> List[PlantRead]:
        offset = (page - 1) * limit
        query = (
            select(Plants)
            .options(selectinload(Plants.plant_type))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        plants = result.scalars().all()
        return [PlantRead.model_validate(p) for p in plants]

    async def get_by_id(self, id: str) -> Optional[PlantRead]:
        query = (
            select(Plants)
            .where(Plants.id == UUID(id))
            .options(selectinload(Plants.plant_type))
        )
        result = await self.db.execute(query)
        plant = result.scalar_one_or_none()
        if plant:
            return PlantRead.model_validate(plant)
        return None

    async def create(self, plant_data: PlantBase) -> PlantRead:
        new_plant = Plants(
            name=plant_data.name,
            typical_days_to_harvest=plant_data.typical_days_to_harvest,
            description=plant_data.description,
            plant_type_id=UUID(plant_data.plant_type_id),
        )
        self.db.add(new_plant)
        await self.db.commit()
        await self.db.refresh(new_plant, attribute_names=["plant_type"])  # Ensure plant_type is refreshed
        return PlantRead.model_validate(new_plant)

    async def update(self, id: str, plant_data: PlantBase) -> Optional[PlantRead]:
        query = (
            update(Plants)
            .where(Plants.id == UUID(id))
            .values(
                name=plant_data.name,
                typical_days_to_harvest=plant_data.typical_days_to_harvest,
                description=plant_data.description,
                plant_type_id=UUID(plant_data.plant_type_id),
                updated_at=datetime.now()
            )
            .returning(Plants)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        plant = result.scalar_one_or_none()
        if plant:
            await self.db.refresh(plant, attribute_names=["plant_type"])  
            return PlantRead.model_validate(plant)
        return None

    async def delete(self, id: str) -> bool:
        query = delete(Plants).where(Plants.id == UUID(id))
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0