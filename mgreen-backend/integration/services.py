from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models import TelegramIntegration
from .schemas import TelegramIntegrationCreate, TelegramIntegrationResponse
from utils.logger import logger
from utils.kafka_client import KafkaProducer
from datetime import datetime, timezone, timedelta
from typing import List 
from datetime import datetime, timedelta

class Integrations:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.kafka_producer = KafkaProducer()

    async def create_telegram_integration(self, telegram_data: TelegramIntegrationCreate) -> TelegramIntegrationResponse:
        """Create a new Telegram integration and notify via Kafka."""
        try:
            # Start Kafka producer
            await self.kafka_producer.start()

            # Begin transaction
            async with self.db.begin() as transaction:
                new_integration = TelegramIntegration(telegram_id=telegram_data.telegram_id)
                self.db.add(new_integration)
                await self.db.flush()  # Ensure ID is assigned without committing yet
                await transaction.commit()  # Explicit commit

            await self.db.refresh(new_integration)

            deliver_time = datetime.now(timezone.utc) + timedelta(seconds=5)
            await self.kafka_producer.send_message(
                telegram_id=str(telegram_data.telegram_id),
                message=f"Successfully integrated with Application, created with ID: {new_integration.id}",
                deliver_at=deliver_time
            )
            logger.info(f"Scheduled integration message for Telegram ID {telegram_data.telegram_id} at {deliver_time.isoformat()}Z")

            return TelegramIntegrationResponse.model_validate(new_integration)

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error creating Telegram integration: {str(e)}")
            raise Exception(f"Failed to create integration: {str(e)}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating Telegram integration: {str(e)}")
            raise Exception(f"Failed to create integration: {str(e)}")

        finally:
            # Always stop the producer
            await self.kafka_producer.stop()
    async def get_telegram_integration(self, telegram_id: int) -> TelegramIntegrationResponse:
        try:
            query = select(TelegramIntegration).where(TelegramIntegration.telegram_id == telegram_id)
            result = await self.db.execute(query)
            integration = result.scalar_one_or_none()

            if not integration:
                raise Exception(f"Telegram integration with ID {telegram_id} not found")

            # await self.kafka_producer.send_message(
            #     telegram_id=str(telegram_id),
            #     message=f"Telegram integration retrieved: {integration.id}"
            # )

            return TelegramIntegrationResponse.model_validate(integration)
        except Exception as e:
            logger.error(f"Error retrieving Telegram integration: {str(e)}")
            raise

    async def get_all_telegram_integrations(self) -> List[TelegramIntegrationResponse]:
        try:
            query = select(TelegramIntegration)
            result = await self.db.execute(query)
            integrations = result.scalars().all()  

            if not integrations:
                logger.info("No Telegram integrations found")
                return []

            # Optional: Send Kafka message for each integration retrieved
            # for integration in integrations:
            #     await self.kafka_producer.send_message(
            #         telegram_id=str(integration.telegram_id),
            #         message=f"Telegram integration retrieved: {integration.id}"
            #     )

            # Convert to list of TelegramIntegrationResponse objects
            return [TelegramIntegrationResponse.model_validate(integration) for integration in integrations]
        except Exception as e:
            logger.error(f"Error retrieving all Telegram integrations: {str(e)}")
            raise

    async def delete_telegram_integration(self, telegram_id: int) -> dict:
        try:
            query = delete(TelegramIntegration).where(TelegramIntegration.telegram_id == telegram_id)
            result = await self.db.execute(query)

            if result.rowcount == 0:
                raise Exception(f"Telegram integration with ID {telegram_id} not found")

            await self.db.commit()

            await self.kafka_producer.send_message(
                telegram_id=str(telegram_id),
                message=f"Telegram integration for ID {telegram_id} deleted"
            )

            return {"message": f"Telegram integration with ID {telegram_id} deleted successfully"}
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting Telegram integration: {str(e)}")
            raise