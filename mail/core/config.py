from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str
    IS_DEVELOPMENT: bool = True
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore

settings = get_settings()