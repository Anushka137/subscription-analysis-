"""
Configuration management for the subscription analytics platform.
Centralizes all configuration settings and environment variables.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Handle Pydantic version compatibility
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback for older Pydantic versions
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        raise ImportError("Pydantic is required. Install with: pip install pydantic pydantic-settings")

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=3306, alias="DB_PORT")
    database: str = Field(default="subscription_analytics", alias="DB_NAME")
    username: str = Field(default="root", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")
    charset: str = Field(default="utf8mb4", alias="DB_CHARSET")
    
    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"  # Ignore extra fields

class APIConfig(BaseSettings):
    """API configuration settings."""
    api_key: str = Field(..., alias="API_KEY_1")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    subscription_api_url: str = Field(default="http://localhost:8000", alias="SUBSCRIPTION_API_URL")
    
    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"  # Ignore extra fields

class ModelConfig(BaseSettings):
    """AI/ML model configuration settings."""
    model_path: str = Field(default="./model", alias="MODEL_PATH")
    semantic_learning_enabled: bool = Field(default=True, alias="SEMANTIC_LEARNING_ENABLED")
    offline_mode: bool = Field(default=True, alias="HF_HUB_OFFLINE")
    
    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"  # Ignore extra fields

class ServerConfig(BaseSettings):
    """Server configuration settings."""
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"  # Ignore extra fields

class Settings(BaseSettings):
    """Main application settings."""
    database: DatabaseConfig = DatabaseConfig()
    api: APIConfig = APIConfig()
    model: ModelConfig = ModelConfig()
    server: ServerConfig = ServerConfig()
    
    # Application paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"
    graphs_dir: Path = base_dir / "generated_graphs"
    
    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"  # Ignore extra fields
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.graphs_dir.mkdir(exist_ok=True)

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings

def validate_config() -> bool:
    """Validate that all required configuration is present."""
    try:
        # Validate API keys
        if not settings.api.api_key:
            print("❌ Error: API_KEY_1 is required")
            return False
        
        if not settings.api.google_api_key:
            print("⚠️ Warning: GOOGLE_API_KEY is not set. Some features may not work.")
        
        # Validate database connection
        if not all([settings.database.host, settings.database.database, 
                   settings.database.username, settings.database.password]):
            print("❌ Error: Database configuration is incomplete")
            return False
        
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False 