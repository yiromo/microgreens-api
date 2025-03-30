from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str

    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_ENDPOINT: str
 
    IS_DEVELOPMENT: bool = True
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300000
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 600000000000
    
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore

settings = get_settings()