import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import get_db
import base64
from datetime import datetime
from typing import Optional, Tuple, List
from .models import Records
import json
from fastapi import HTTPException
from .schemas import RecordsBase
from seedbeds.models import Seedbeds
from seedbeds.services import SeedbedsService
from seedbeds.schemas import SeedbedResponseFull
from llm.request import LLMRequest
from llm.schemas import LLMTemperature, AIModelType
from utils.logger import logger
from core.ai_config import OPENAI_CLIENT
import imghdr


class RecordsService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = OPENAI_CLIENT

    async def get_all_records_by_id(
        self,
        seedbed_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Records], int]:
        try:
            offset = (page - 1) * page_size
            
            query = select(Records).where(Records.soilId == seedbed_id).offset(offset).limit(page_size)
            result = await self.db.execute(query)
            records = result.scalars().all()

            count_query = select(func.count()).select_from(Records).where(Records.soilId == seedbed_id)
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            return records, total_count
            
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении записей: {str(e)}")
            raise e
        

    async def llm_request_record(self, seedbed: SeedbedResponseFull, record: RecordsBase):
        try:
            image_str = record.photo_link
            
            if not image_str:
                logger.error("Missing image data")
                raise ValueError("Image data is required for analysis")

            if not image_str.startswith("data:image/"):
                raise HTTPException(status_code=400, detail="Invalid image format")
            
            try:
                header, base64_data = image_str.split(",", 1)
                image = base64.b64decode(base64_data)
            except Exception as e:
                logger.error(f"Failed to decode base64 image: {str(e)}")
                raise ValueError(f"Invalid base64 image data: {str(e)}")
            
            if not hasattr(self, 'client') or self.client is None:
                logger.error("LLM client is not initialized")
                raise ValueError("LLM client initialization failed")
                    
            logger.info("Creating LLM request with plant analysis prompt")
            llm = LLMRequest(
                client=self.client,
                model=AIModelType.GPT4O,
                temperature=LLMTemperature.LOWEST
            )
            
            system_message = f"""
    You are an expert botanist specializing in microgreen cultivation and plant health assessment. Analyze the provided image to identify the microgreens' growth stage and health status.

    # SEEDBED DATA
    - Soil Count: {seedbed.soil_number}
    - Planting Date: {str(seedbed.date_planted)}
    - Soil Type: {seedbed.type_of_soil}
    - Plant Name: {seedbed.plant_name}
    - Plant Classification: {seedbed.plant.plant_type.name}

    # CURRENT CONDITIONS
    - Water Temperature: {record.water_temperature}°C
    - Air Temperature: {record.air_temperature}°C
    - Air Humidity: {record.air_humidity}%
    - Light Level: {record.light_level} lux
    - Plant Height: {record.height_plant} cm

    # ANALYSIS REQUIREMENTS
    1. Examine the image for microgreen development stage and health indicators
    2. Assess if growing conditions are optimal for this specific plant type
    3. Provide actionable recommendations to improve growth or correct issues
    4. Predict optimal harvest date based on current growth rate, conditions and provided image

    RESPONSE REQUIREMENTS:
    1. Have to be strict json
    2. If the image doesn't contains any microgreen or seedbed, then make "day_when_harvest": null and "message": "Need to send microgreen or seedbed"

    # RESPONSE FORMAT
    Your response must be valid JSON with exactly this structure:
    ```json
    {{
    "message": "Detailed analysis with observations and recommendations",
    "day_when_harvest": datetime with timezone | null
    }}
    ```

    The "message" should include your key observations and specific recommendations.
    The "day_when_harvest" should be a date string or null if harvest timing cannot be determined.
    """
            llm.add_system_message(system_message)

            prompt = "Provide a complete analysis of the microgreens shown in this image based on the provided data."

            try:
                response_text = await llm.send_with_image(image, prompt)
                logger.info("Received LLM response, processing results")
                
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.rfind("```")
                    if json_end > json_start:
                        response_text = response_text[json_start:json_end].strip()
                
                try:
                    response_data = json.loads(response_text)
                    print(response_data)
                    
                    if "message" not in response_data:
                        raise ValueError("Missing required 'message' field in response")
                    
                    return response_data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {str(e)}")
                    logger.error(f"Raw response: {response_text}")
                    raise ValueError(f"LLM returned invalid JSON format: {str(e)}")
                    
            except Exception as llm_error:
                logger.error(f"LLM communication error: {str(llm_error)}", exc_info=True)
                raise ValueError(f"Failed to get analysis from AI model: {str(llm_error)}")

        except Exception as e:
            logger.error(f"Error in microgreen analysis: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Image processing error: {str(e)}"
            )
        
    async def record_analytics(self, records: RecordsBase, seedbed_id: int):
        try: 
            seedbeds_service = SeedbedsService(self.db)
            seedbed_dict = await seedbeds_service.get_seedbed_by_id(seedbed_id)
            if not seedbed_dict:
                return "Provide SoilId"
            
            seedbed = SeedbedResponseFull(**seedbed_dict) 
            logger.info(seedbed)
            
            if not seedbed:
                raise ValueError(f"Seedbed with ID {seedbed_id} not found")
            
            response = await self.llm_request_record(seedbed, records)
            
            if response.get('day_when_harvest'):
                try:
                    harvest_date_str = response.get('day_when_harvest')
                    harvest_date = datetime.fromisoformat(harvest_date_str)
                    await seedbeds_service.update_seedbed_date_harvested(seedbed_id, harvest_date)
                    logger.info(f"Updated seedbed {seedbed_id} with harvest date: {harvest_date}")
                except ValueError as parse_error:
                    logger.error(f"Failed to parse harvest date '{harvest_date_str}': {str(parse_error)}")
                    raise ValueError(f"Invalid harvest date format: {str(parse_error)}")
                except Exception as update_error:
                    logger.error(f"Failed to update harvest date: {str(update_error)}")
            
            if response.get('message'):
                return response.get('message')
            else:
                return "Analysis completed, but no specific recommendations available"

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}", exc_info=True)
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid data: {str(ve)}"
            )
        except Exception as e:
            logger.error(f"Analytics processing error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to analyze plant data: {str(e)}"
            )

    
    async def add_record_by_id(
        self,
        records: RecordsBase,
        seedbed_id: int
    ) -> Optional[Records]:
        try:           
            new_record = Records(
                water_temperature=records.water_temperature,
                air_temperature=records.air_temperature,
                air_humidity=records.air_humidity,
                light_level=records.light_level,
                height_plant=records.height_plant,
                photo_link=records.photo_link,
                soilId=seedbed_id
            )
            
            self.db.add(new_record)
            await self.db.commit()
            await self.db.refresh(new_record)
            
            return new_record
            
        except IntegrityError as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            await self.db.rollback()
            raise e
        
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при добавлении записи: {str(e)}")
            await self.db.rollback()
            raise e