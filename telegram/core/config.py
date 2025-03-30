from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    
    KAFKA_BOOTSTRAP_SERVERS: str = "192.168.11.11:9092"  
    KAFKA_GROUP_ID: str = "telegram_bot_group"
    KAFKA_TOPIC: str = "telegram_messages"

    ADMINS: list[int] = [7258936037]
    
    IS_DEVELOPMENT: bool = False

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()  

settings = get_settings()