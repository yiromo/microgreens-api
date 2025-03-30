from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from plants.models import Plants
from fastapi import UploadFile, HTTPException
from llm.request import LLMRequest
import json
from core.ai_config import OPENAI_CLIENT
from plants.plants_type.plants_type_service import PlantsTypeService
from llm.schemas import LLMTemperature, MAXTOKENS, AIModelType
from .plants_schemas import PlantBase, PlantRead, PlantListResponse
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import math
import imghdr
from utils.logger import logger

class PlantsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = OPENAI_CLIENT


    async def get_all(self, page: int = 1, page_size: int = 10) -> PlantListResponse:
        offset = (page - 1) * page_size
        
        query = (
            select(Plants)
            .options(selectinload(Plants.plant_type))
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        plants = result.scalars().all()
        
        total_query = select(func.count(Plants.id))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()

        page_count = math.ceil(total / page_size) if total > 0 else 0

        return PlantListResponse(
            items=[PlantRead.model_validate(p) for p in plants],
            page_size=page_size,
            page_count=page_count
        )

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
        await self.db.refresh(new_plant, attribute_names=["plant_type"])
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
    
    async def create_by_image(self, image: bytes) -> dict:
        try:
            logger.info("Starting create_by_image in PlantsService")
            plants_type_service = PlantsTypeService(self.db)
            
            logger.info(f"Read {len(image)} bytes from image")
            
            if not image:
                logger.error("Empty image file")
                raise ValueError("Empty image file")

            img_type = imghdr.what(None, image)
            logger.info(f"Detected image type: {img_type}")
            
            if not img_type:
                logger.error("Could not determine image format")
                raise ValueError("Invalid image format")

            logger.info("Fetching plant types")
            plants_types = await plants_type_service.get_all(page=1, limit=10000000)
            logger.info(f"Found {len(plants_types)} plant types")

            if not hasattr(self, 'client') or self.client is None:
                logger.error("LLM client is not initialized")
                raise ValueError("LLM client is not initialized")
                
            logger.info("Creating LLM request")
            llm = LLMRequest(
                client=self.client,
                model=AIModelType.GPT4O,
                temperature=LLMTemperature.LOWEST
            )

            plants_types_str = str(plants_types)
            if len(plants_types_str) > 500:
                plants_types_str = plants_types_str[:500] + "..."
            
            logger.info(f"Plants types for LLM: {plants_types_str}")

            system_message = f"""
You are an expert in plant identification, specializing in microgreens. Your task is to analyze an image and identify any microgreens present. Use the provided list of plant types to match identified microgreens with their `plant_type_id`.

**Instructions:**
1. **Input Analysis:**
   - Examine the image for microgreens (small, edible plants harvested at an early stage).
   - If no microgreens are detected, return a JSON response with an error message.

2. **Matching Plant Types:**
   - Use the following list of plant types: {plants_types}.
   - For each identified microgreen, select the appropriate `plant_type_id` from this list based on the plant's characteristics.
   - If a microgreen doesn't match any plant type, use a default or closest match and note it in the description.

3. **Response Format:**
   - Always return a dictionary in this exact structure:
     ```json
     {{
       "error": null | "string",
       "list_of_items": [
         {{
           "name": "string",               
           "typical_days_to_harvest": int, 
           "description": "string",        
           "plant_type_id": "string"       
         }}
       ]
     }}
     ```
"""
            
            logger.info("Adding system message to LLM")
            llm.add_system_message(system_message)

            prompt = """
Analyze the photo. Follow the system prompt instructions.
"""
            logger.info("Sending image to LLM for analysis")
            
            try:
                response_text = await llm.send_with_image(
                    image,
                    prompt
                )
                logger.info("Received response from LLM")
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.rfind("```")
                    if json_end > json_start:
                        response_text = response_text[json_start:json_end].strip()
                
                log_response = response_text
                if len(response_text) > 1000:
                    log_response = response_text[:1000] + "..."
                logger.info(f"LLM response: {log_response}")
                
                try:
                    response_data = json.loads(response_text)
                    if "list_of_items" not in response_data or not isinstance(response_data["list_of_items"], list):
                        raise ValueError("Invalid response structure: missing or invalid 'list_of_items'")
                    return response_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {str(e)}")
                    logger.error(f"Invalid JSON: {response_text}")
                    raise ValueError(f"Failed to parse LLM response: {str(e)}")
                    
            except Exception as llm_error:
                logger.error(f"Error communicating with LLM: {str(llm_error)}", exc_info=True)
                raise ValueError(f"Error communicating with LLM: {str(llm_error)}")

        except Exception as e:
            logger.error(f"Error in create_by_image: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка при обработке изображения: {str(e)}"
            )

    async def create_from_image_analysis(self, image) -> List[PlantRead]:
        try:
            analysis_result = await self.create_by_image(image)
            
            if analysis_result.get("error"):
                raise ValueError(f"Image analysis failed: {analysis_result['error']}")
                
            list_of_items = analysis_result.get("list_of_items", [])
            if not list_of_items:
                return []  
                
            created_plants = []
            for item in list_of_items:
                try:
                    plant_data = PlantBase(
                        name=item["name"],
                        typical_days_to_harvest=item["typical_days_to_harvest"],
                        description=item["description"],
                        plant_type_id=item["plant_type_id"]
                    )
                    
                    new_plant = await self.create(plant_data)
                    created_plants.append(new_plant)
                    
                except KeyError as e:
                    logger.error(f"Missing required field in item: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Failed to create plant from item {item}: {str(e)}")
                    continue
                    
            return created_plants
            
        except Exception as e:
            logger.error(f"Error in create_from_image_analysis: {str(e)}", exc_info=True)
            raise