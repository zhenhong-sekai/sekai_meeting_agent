from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://yunwu.ai/v1"
    MODEL_NAME: str = "gpt-4o"
    
    # Notion settings
    NOTION_TOKEN: str
    
    # Zoom settings
    ZOOM_ACCOUNT_ID: str
    ZOOM_CLIENT_ID: str
    ZOOM_CLIENT_SECRET: str
    ZOOM_WEBHOOK_USER: str
    ZOOM_WEBHOOK_PASS: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
