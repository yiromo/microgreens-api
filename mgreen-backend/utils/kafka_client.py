import json
import asyncio
from aiokafka import AIOKafkaProducer
from utils.logger import logger
from core.config import settings
from datetime import datetime

class KafkaProducer:
    def __init__(self, topic_name="telegram_messages"):
        self.topic_name = topic_name
        self.producer = None
    
    async def start(self):
        """Start the Kafka producer."""
        logger.info(f"Starting Kafka producer for topic: {self.topic_name}")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info(f"Kafka producer started successfully")
    
    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            logger.info("Stopping Kafka producer")
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def send_message(self, telegram_id: str, message: str, deliver_at: datetime = None):
        try:
            if not self.producer:
                raise ValueError("Producer not started. Call start() first.")
            
            msg_data = {
                "telegram_id": telegram_id,
                "message": message
            }
            if deliver_at:
                msg_data["deliver_at"] = deliver_at.isoformat() + "Z"
            
            logger.info(f"Sending message to Kafka: {msg_data}")
            await self.producer.send(self.topic_name, value=msg_data)
            logger.info(f"Message sent to Kafka topic {self.topic_name}")
        
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {str(e)}")
            raise

kafka_producer = KafkaProducer()