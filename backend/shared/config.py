"""Shared configuration settings for all EVY services."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    env: str = "development"
    
    # Service Ports
    sms_gateway_port: int = 8000
    message_router_port: int = 8001
    llm_inference_port: int = 8002
    rag_service_port: int = 8003
    privacy_filter_port: int = 8004
    logging_service_port: int = 8006
    api_gateway_port: int = 8000
    
    # LLM Configuration
    llm_provider: str = "ollama"  # openai, ollama, tiny, or bitnet
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://host.docker.internal:11434"
    
    # Model Configuration
    default_model: str = "tinyllama"
    tiny_model: str = "tinyllama"
    bitnet_model: str = "bitnet-2b"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: str = "/data/models/embedding_cache"
    rag_min_similarity: float = 0.5
    
    # Database
    database_url: str = "sqlite:///data/evy.db"
    
    # Vector Database
    chroma_persist_dir: str = "/data/chroma"
    
    # SMS Configuration
    sms_device: str = "/dev/ttyUSB0"
    sms_gps_device: str = "/dev/ttyUSB1"
    sms_baud_rate: int = 115200

    # LoRa / edge hardware
    lora_frequency_mhz: float = 915.0
    lora_cs_pin: int = 25
    lora_dio0_pin: int = 4
    lora_reset_pin: int = 17
    deployment_region: str = "us"

    # Runtime behavior
    local_first_routing: bool = True
    
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


