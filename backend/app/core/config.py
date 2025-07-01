from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Customer Support AI"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # External APIs
    GEMINI_API_KEY: str
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_JWKS_URL: str
    
    # CORS - Use Union to allow string or list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:3001"
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated format
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS_ORIGINS format: {v}")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()