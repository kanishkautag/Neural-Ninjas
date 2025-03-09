import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys and URLs
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # App settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8080"))
    
    class Config:
        env_file = ".env"
        extra = "allow"  # This allows extra fields

settings = Settings()