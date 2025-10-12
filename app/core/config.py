"""
Core configuration module
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Dict


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://username:password@postgres:5432/localizer"
    
    # Security
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600
    
    # Redis & Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Storage
    STORAGE_DIR: str = "storage"
    UPLOAD_DIR: str = "storage/uploads"
    OUTPUT_DIR: str = "storage/outputs"
    MODEL_DIR: str = "models"
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Indian Language Localizer"
    
    # Models
    TRANSLATION_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    WHISPER_MODEL: str = "openai/whisper-large-v3"
    TTS_MODEL: str = "tts_models/en/vctk/vits"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Supported Indian Languages (22)
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "as": "Assamese",
    "bn": "Bengali",
    "brx": "Bodo",
    "doi": "Dogri",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ks": "Kashmiri",
    "mai": "Maithili",
    "ml": "Malayalam",
    "mni": "Manipuri",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "sat": "Santali",
    "sd": "Sindhi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu"
}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

