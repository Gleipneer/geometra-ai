"""Memory configuration settings."""

from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator

class MemorySettings(BaseSettings):
    """Settings for memory components."""
    
    # ChromaDB Settings
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_OPENAI_API_KEY: Optional[str] = None
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL_SECONDS: int = 600
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    FALLBACK_OPENAI_API_KEY: Optional[str] = None
    
    # Model Settings
    DEFAULT_MODEL: str = "gpt-4"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    # API Settings
    API_KEYS: str = ""  # Kommaseparerad sträng
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Environment Settings
    ENV: str = "development"
    RAILWAY_PROJECT_NAME: str = "geometra-ai"
    RAILWAY_ENVIRONMENT: str = "staging"
    
    # System Settings
    ENABLE_SYSTEM_CHECK: bool = True
    SYSTEM_CHECK_INTERVAL_SECONDS: int = 300
    
    # CI Settings
    CI_COMMIT_TAG: str = "latest"
    CI_DEPLOY_BRANCH: str = "main"
    
    # Memory Settings
    MEMORY_CONTEXT_WINDOW: int = 10
    DEBUG_MODE: bool = False
    
    @field_validator("API_KEYS")
    @classmethod
    def parse_api_keys(cls, v: str) -> List[str]:
        """Parse comma-separated API keys into a list."""
        if not v:
            return []
        return [key.strip() for key in v.split(",")]
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        extra = "allow"  # Tillåt extra fält i .env-filen 