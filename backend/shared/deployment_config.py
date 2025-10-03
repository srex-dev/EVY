"""Deployment configuration for lilEVY vs bigEVY nodes."""
from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """EVY node types."""
    LILEVY = "lilevy"  # Edge SMS node
    BIGEVY = "bigevy"  # Central processing node


class HardwareProfile(BaseModel):
    """Hardware profile for different node types."""
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    gpu_available: bool = False
    power_consumption_w: int
    solar_capable: bool = False


class LLMConfig(BaseModel):
    """LLM configuration for different node types."""
    model_size_range: str  # e.g., "125M-350M" or "7B-13B"
    quantization: str  # "4bit", "8bit", "16bit", "32bit"
    max_tokens: int
    response_time_target: int  # seconds
    batch_processing: bool = False


class RAGConfig(BaseModel):
    """RAG configuration for different node types."""
    vector_db_type: str
    max_documents: int
    embedding_model: str
    search_method: str  # "vector", "hybrid", "text"
    cache_size_mb: int


class NetworkConfig(BaseModel):
    """Network configuration for different node types."""
    internet_required: bool
    peer_discovery: bool
    mesh_network: bool
    sync_interval_hours: int


class DeploymentProfile(BaseModel):
    """Complete deployment profile for a node type."""
    node_type: NodeType
    hardware: HardwareProfile
    llm: LLMConfig
    rag: RAGConfig
    network: NetworkConfig
    services: List[str]
    features: Dict[str, bool]


# lilEVY Configuration (Edge SMS Node)
LILEVY_PROFILE = DeploymentProfile(
    node_type=NodeType.LILEVY,
    hardware=HardwareProfile(
        cpu_cores=4,
        memory_gb=8,
        storage_gb=128,
        gpu_available=False,
        power_consumption_w=15,
        solar_capable=True
    ),
    llm=LLMConfig(
        model_size_range="125M-350M",
        quantization="4bit",
        max_tokens=512,
        response_time_target=10,
        batch_processing=False
    ),
    rag=RAGConfig(
        vector_db_type="chromadb",
        max_documents=10000,
        embedding_model="all-MiniLM-L6-v2",
        search_method="hybrid",
        cache_size_mb=500
    ),
    network=NetworkConfig(
        internet_required=False,
        peer_discovery=True,
        mesh_network=True,
        sync_interval_hours=24
    ),
    services=[
        "sms_gateway",
        "message_router", 
        "llm_inference_tiny",
        "rag_service_local",
        "privacy_filter",
        "local_storage"
    ],
    features={
        "offline_capable": True,
        "solar_powered": True,
        "gsm_interface": True,
        "local_knowledge": True,
        "tiny_llm": True,
        "peer_sync": True,
        "emergency_mode": True
    }
)

# bigEVY Configuration (Central Processing Node)
BIGEVY_PROFILE = DeploymentProfile(
    node_type=NodeType.BIGEVY,
    hardware=HardwareProfile(
        cpu_cores=16,
        memory_gb=64,
        storage_gb=2000,
        gpu_available=True,
        power_consumption_w=500,
        solar_capable=False
    ),
    llm=LLMConfig(
        model_size_range="7B-13B",
        quantization="8bit",
        max_tokens=2048,
        response_time_target=30,
        batch_processing=True
    ),
    rag=RAGConfig(
        vector_db_type="chromadb",
        max_documents=1000000,
        embedding_model="all-mpnet-base-v2",
        search_method="vector",
        cache_size_mb=10000
    ),
    network=NetworkConfig(
        internet_required=True,
        peer_discovery=True,
        mesh_network=False,
        sync_interval_hours=1
    ),
    services=[
        "model_manager",
        "llm_inference_large",
        "rag_service_global",
        "analytics_service",
        "sync_service",
        "update_manager",
        "load_balancer",
        "monitoring_service"
    ],
    features={
        "offline_capable": False,
        "solar_powered": False,
        "gsm_interface": False,
        "local_knowledge": False,
        "tiny_llm": False,
        "peer_sync": True,
        "emergency_mode": False,
        "heavy_processing": True,
        "global_sync": True,
        "model_updates": True,
        "analytics": True
    }
)

# Configuration registry
DEPLOYMENT_PROFILES = {
    NodeType.LILEVY: LILEVY_PROFILE,
    NodeType.BIGEVY: BIGEVY_PROFILE
}


def get_deployment_profile(node_type: NodeType) -> DeploymentProfile:
    """Get deployment profile for a specific node type."""
    return DEPLOYMENT_PROFILES[node_type]


def get_supported_services(node_type: NodeType) -> List[str]:
    """Get list of services supported by a node type."""
    return get_deployment_profile(node_type).services


def is_feature_enabled(node_type: NodeType, feature: str) -> bool:
    """Check if a feature is enabled for a node type."""
    profile = get_deployment_profile(node_type)
    return profile.features.get(feature, False)


def get_node_capabilities(node_type: NodeType) -> Dict[str, Any]:
    """Get comprehensive capabilities for a node type."""
    profile = get_deployment_profile(node_type)
    return {
        "hardware": profile.hardware.dict(),
        "llm": profile.llm.dict(),
        "rag": profile.rag.dict(),
        "network": profile.network.dict(),
        "services": profile.services,
        "features": profile.features
    }
