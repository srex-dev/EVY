"""Shared configuration settings for all EVY services."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    env: str = "development"
    
    # Service Ports
    sms_gateway_port: int = 8001
    message_router_port: int = 8002
    llm_inference_port: int = 8003
    rag_service_port: int = 8004
    privacy_filter_port: int = 8005
    logging_service_port: int = 8006
    api_gateway_port: int = 8000
    
    # LLM Configuration
    llm_provider: str = "openai"  # openai or ollama
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    
    # Model Configuration
    default_model: str = "gpt-4"
    tiny_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    
    # Database
    database_url: str = "postgresql://evy:evy_password@postgres:5432/evy_db"
    
    # Vector Database
    chroma_persist_dir: str = "/data/chroma"
    
    # SMS Configuration
    sms_device: str = "/dev/ttyUSB0"
    sms_baud_rate: int = 115200
    
    # Security
    secret_key: str = "change_this_secret_key_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    max_sms_per_minute: int = 10
    max_sms_per_hour: int = 100
    
    # Monitoring
    prometheus_port: int = 9090
    grafana_port: int = 3001
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


