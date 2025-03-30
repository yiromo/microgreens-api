
from pydantic import BaseModel
from typing import List

class MessageItem(BaseModel):
    telegram_id: int
    message: str

class MessageBatch(BaseModel):
    messages: List[MessageItem]