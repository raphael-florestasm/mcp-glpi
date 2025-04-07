"""
Configuration settings for the MCP GLPI Server.
This module loads and validates environment variables.
"""

import os
from typing import List
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # GLPI Configuration
    GLPI_URL: str
    GLPI_APP_TOKEN: str
    GLPI_USER_TOKEN: str
    GLPI_DEFAULT_ENTITY_ID: int = 0
    
    # Server Configuration
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8000
    MCP_DEBUG: bool = False
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Cache Configuration
    CACHE_TTL: int = 300  # 5 minutes in seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/mcp-server.log"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("GLPI_URL")
    def validate_glpi_url(cls, v):
        """Validate GLPI URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("GLPI_URL must start with http:// or https://")
        return v.rstrip("/")
    
    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v):
        """Validate CORS origins format."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 