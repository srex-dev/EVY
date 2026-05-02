"""Shared configuration settings for all EVY services."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
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
    llm_provider: str = "bitnet"  # bitnet, openai, ollama, or tiny
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://host.docker.internal:11434"
    llm_auto_pull_models: bool = False
    
    # Model Configuration
    default_model: str = "bitnet-b1.58-2B-4T"
    tiny_model: str = "tinyllama"
    bitnet_model: str = "bitnet-b1.58-2B-4T"
    bitnet_cpp_dir: str = "/opt/bitnet.cpp"
    bitnet_model_path: str = "/models/bitnet/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
    bitnet_run_script: Optional[str] = None
    bitnet_python_executable: Optional[str] = None
    bitnet_threads: int = 2
    bitnet_context_tokens: int = 512
    bitnet_n_predict: int = 80
    bitnet_chat_mode: bool = True
    bitnet_allow_fallback: bool = False
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: str = "/data/models/embedding_cache"
    rag_min_similarity: float = 0.5
    
    # Database
    database_url: str = "sqlite:///data/evy.db"
    
    # Vector Database
    chroma_persist_dir: str = "/data/chroma"
    rag_backend: str = "chroma"  # chroma or sqlite
    sqlite_rag_enabled: bool = False
    sqlite_rag_db_path: str = "/data/lilevy/sqlite_rag.db"
    knowledge_pack_require_signature: bool = False
    
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

    # Edge service URLs (overridable for container networking)
    sms_gateway_url: str = "http://localhost:8000"
    message_router_url: str = "http://localhost:8001"
    llm_inference_url: str = "http://localhost:8002"
    rag_service_url: str = "http://localhost:8003"
    privacy_filter_url: str = "http://localhost:8004"
    
    # Security
    secret_key: str = "change_this_secret_key_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    max_sms_per_minute: int = 10
    max_sms_per_hour: int = 100

    # Edge load envelope and backpressure
    edge_target_inbound_sms_per_minute: int = 20
    edge_target_p95_response_ms: int = 12000
    edge_target_max_queue_depth: int = 500
    edge_target_memory_ceiling_mb: int = 4096
    sms_inbound_queue_maxsize: int = 500
    sms_outbound_queue_maxsize: int = 1000
    sms_forward_max_retries: int = 3
    sms_forward_retry_backoff_seconds: int = 2
    sms_router_timeout_seconds: float = 15.0
    llm_request_timeout_seconds: float = 20.0
    llm_max_inflight_requests: int = 2
    llm_max_loaded_models: int = 2
    rag_chunk_size_chars: int = 600
    rag_chunk_overlap_chars: int = 120
    
    # Monitoring
    prometheus_port: int = 9090
    grafana_port: int = 3001
    

# Global settings instance
settings = Settings()


