from fastapi import FastAPI
import uvicorn
import asyncio
import threading
from bot import bot, logger
from kafka_client import kafka_consumer
from core.config import settings

async def run_bot_polling():
    logger.info("Starting Telegram bot polling")
    await bot.polling(non_stop=True)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(asyncio.gather(
            run_bot_polling(),
            kafka_consumer.start()
        ))
    except Exception as e:
        logger.error(f"Error in bot thread: {str(e)}")
    finally:
        loop.close()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Telegram bot and Kafka consumer in a separate thread")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  
    bot_thread.start()
    logger.info("Bot thread started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Kafka consumer")
    await kafka_consumer.stop()

@app.get("/")
async def root():
    return {"status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)