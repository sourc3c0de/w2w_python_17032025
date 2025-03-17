import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PORT: str = os.getenv("PORT", "8000")
    APP_NAME: str = "Whats2Want API"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/whats2want")
    
    # Whatsapp API settings
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "your-verify-token")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "your-access-token")
    WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "your-phone-id")
    
    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()