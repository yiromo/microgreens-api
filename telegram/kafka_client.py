import json
import asyncio
from aiokafka import AIOKafkaConsumer
from bot import bot, logger
from core.config import settings
from datetime import datetime, timezone

class KafkaConsumer:
    def __init__(self, topic_name="telegram_messages"):
        self.topic_name = topic_name
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Start the Kafka consumer."""
        logger.info(f"Starting Kafka consumer for topic: {self.topic_name}")
        self.consumer = AIOKafkaConsumer(
            self.topic_name,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',  
            enable_auto_commit=True
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"Kafka consumer started successfully")
        
        asyncio.create_task(self.process_messages())
    
    async def stop(self):
        """Stop the Kafka consumer."""
        if self.consumer and self.running:
            logger.info("Stopping Kafka consumer")
            self.running = False
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def process_messages(self):
        try:
            async for msg in self.consumer:
                try:
                    data = msg.value
                    if isinstance(data, dict):
                        data = [data]
                    
                    for item in data:
                        if 'telegram_id' not in item or 'message' not in item:
                            logger.warning(f"Invalid message format: {item}")
                            continue
                        
                        deliver_at = item.get('deliver_at')
                        if deliver_at:
                            try:
                                if deliver_at.endswith('Z'):
                                    deliver_at = deliver_at[:-1] 
                                deliver_time = datetime.fromisoformat(deliver_at)
                                now = datetime.now(timezone.utc)
                                delay_seconds = (deliver_time - now).total_seconds()
                                logger.info(f"Msg: {item['message'][:50]}..., deliver_at: {deliver_at}, now: {now.isoformat()}Z, delay: {delay_seconds}s")
                                if delay_seconds > 0:
                                    logger.info(f"Delaying by {delay_seconds}s until {deliver_time}")
                                    await asyncio.sleep(delay_seconds)
                                elif delay_seconds < -10:
                                    logger.warning(f"Overdue by {-delay_seconds}s, sending anyway: {item['message'][:50]}...")
                                else:
                                    logger.info(f"Ready or slightly late ({delay_seconds}s), sending now")
                            except ValueError as e:
                                logger.error(f"Invalid deliver_at format: {deliver_at}, error: {str(e)}")
                                continue
                        
                        logger.info(f"Sending to Telegram ID: {item['telegram_id']}")
                        await bot.send_message(item['telegram_id'], item['message'])
                        await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error processing Kafka msg: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {str(e)}")
            if self.running:
                await asyncio.sleep(5)
                asyncio.create_task(self.process_messages())

kafka_consumer = KafkaConsumer()