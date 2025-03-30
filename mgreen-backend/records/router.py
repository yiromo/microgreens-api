import logging
import mimetypes
from fastapi import APIRouter, File, HTTPException, Path, Query, Response, Depends, UploadFile
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import CommonDependencies
from utils.token import get_token
from fastapi import status
from sqlalchemy.exc import IntegrityError
from .service import RecordsService
from .schemas import *
from utils.minio_service import bucket_images
import base64
import io
from uuid import uuid4
from utils.logger import logger
import traceback


router = APIRouter(
    prefix="/record",
    dependencies=[Depends(get_token)],
    tags=["Records"]
)


@router.get("/records/{seedbed_id}", response_model=GetAllRecordsResponse)
async def get_all_record(
    seedbed_id: int = Path(..., ge=1, description="ID почвы"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    commons: CommonDependencies = Depends()
):  
    db: AsyncSession = commons.db
    records_service = RecordsService(db)

    try:
        records, total_count = await records_service.get_all_records_by_id(seedbed_id, page, page_size)

        page_count = (total_count + page_size - 1) // page_size
        
        return {
            "records": records,
            "page": page,
            "page_size": page_size,
            "page_count": page_count
        }
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при получении записей: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей: {str(e)}"
        )
    
    
@router.post("/record/{seedbed_id}", response_model=AddRecordResponse)
async def add_record_by_id(
    records: RecordsBase,
    seedbed_id: int = Path(..., ge=1, description="ID почвы"),
    commons: CommonDependencies = Depends(),
):  
    db: AsyncSession = commons.db   
    records_service = RecordsService(db)

    original_photo = records.photo_link

    try:
        if records.photo_link and records.photo_link.startswith("data:image/"):
            header, base64_data = records.photo_link.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]
            extension = mimetypes.guess_extension(mime_type) or ".png"

            try:
                photo_data = base64.b64decode(base64_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Некорректные данные изображения: {str(e)}"
                )
            
            filename = f"{uuid4()}{extension}"
            
            try:
                bucket_images.upload_file(photo_data, filename)
                photo_url = bucket_images.get_file_url(filename)
                
                records.photo_link = photo_url

               
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при загрузке изображения: {str(e)}"
                )
            
        records_for_ai = RecordsBase(**records.model_dump())
        records_for_ai.photo_link = original_photo

        message = await records_service.record_analytics(records_for_ai, seedbed_id)
        new_record = await records_service.add_record_by_id(records, seedbed_id)

        return {
            "message": message,
            "record": new_record
        }
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при добавлении записи: {str(e)}"
        )
    except Exception as e:
        tb = traceback.format_exc() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении записи: {str(e)}\nТрассировка:\n{tb}"
        )
