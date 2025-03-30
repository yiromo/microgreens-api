from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class TelegramIntegrationBase(BaseModel):
    telegram_id: int

class TelegramIntegrationCreate(TelegramIntegrationBase):
    pass

class TelegramIntegrationResponse(TelegramIntegrationBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  