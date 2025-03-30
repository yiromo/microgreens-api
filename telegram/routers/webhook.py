from schemas.message import MessageItem
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import asyncio
from bot import bot, logger

router = APIRouter()

@router.post("/webhook")
async def process_webhook(message_batch: List[MessageItem], background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive and process batch messages.
    Sends each message to the corresponding Telegram user ID.
    
    Expected format:
    [
        {"telegram_id": 123456, "message": "Hello user 1"}, 
        {"telegram_id": 789012, "message": "Hello user 2"}
    ]
    """
    if not message_batch:
        raise HTTPException(status_code=400, detail="Empty message batch received")
    
    background_tasks.add_task(process_messages, message_batch)
    
    return {"status": "processing", "message": f"Processing {len(message_batch)} messages"}

async def process_messages(message_batch: List[MessageItem]):
    for item in message_batch:
        try:
            logger.info(f"Sending message to Telegram ID: {item.telegram_id}")
            await bot.send_message(item.telegram_id, item.message)
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error sending message to {item.telegram_id}: {str(e)}")