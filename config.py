import os
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """애플리케이션 필수 설정 클래스"""
    
    # OpenAI Configuration (Required)
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Application Configuration
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")
    
    # Security Configuration
    secret_key: str = Field("change-this-secret-key", env="SECRET_KEY")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Storage Configuration
    storage_type: str = Field("memory", env="STORAGE_TYPE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """설정 객체를 캐시하여 반환"""
    return Settings()

# 전역 설정 인스턴스
settings = get_settings()