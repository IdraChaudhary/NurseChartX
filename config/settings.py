import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "NurseChartX"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Keys (Optional - can be provided at runtime)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    cohere_api_key: Optional[str] = Field(None, env="COHERE_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # OCR Settings
    ocr_engine: str = Field(default="easyocr", env="OCR_ENGINE")
    supported_languages: list = Field(default=["en"])
    
    # Model Settings
    openai_model: str = Field(default="gpt-3.5-turbo")
    cohere_model: str = Field(default="command")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    
    # Processing Settings
    max_file_size_mb: int = Field(default=10)
    allowed_extensions: list = Field(default=[".jpg", ".jpeg", ".png", ".bmp", ".tiff"])
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
