"""
Offline Knowledge Base Configuration for lilEVY
Defines the structure and priorities for offline RAG knowledge
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class Priority(Enum):
    CRITICAL = "critical"  # Life-saving information
    HIGH = "high"         # Essential services
    MEDIUM = "medium"     # Important information
    LOW = "low"          # Nice to have

class ResponseType(Enum):
    EMERGENCY = "emergency"
    MEDICAL_EMERGENCY = "medical_emergency"
    WEATHER_EMERGENCY = "weather_emergency"
    UTILITY_EMERGENCY = "utility_emergency"
    CONTACT_INFO = "contact_info"
    SERVICE_INFO = "service_info"
    WEATHER_ADVICE = "weather_advice"
    TRANSPORTATION_INFO = "transportation_info"
    TECH_SUPPORT = "tech_support"
    HOME_REPAIR = "home_repair"
    CRISIS_SUPPORT = "crisis_support"

@dataclass
class KnowledgeCategory:
    """Configuration for a knowledge category"""
    name: str
    priority: Priority
    max_entries: int
    description: str
    response_type: ResponseType
    character_limit: int = 160  # SMS character limit

# Offline Knowledge Categories Configuration
OFFLINE_KNOWLEDGE_CATEGORIES = {
    "emergency": KnowledgeCategory(
        name="Emergency Procedures",
        priority=Priority.CRITICAL,
        max_entries=50,
        description="Life-critical emergency procedures and contacts",
        response_type=ResponseType.EMERGENCY,
        character_limit=140  # Shorter for emergency responses
    ),
    "weather_safety": KnowledgeCategory(
        name="Weather Safety",
        priority=Priority.CRITICAL,
        max_entries=30,
        description="Weather-related safety procedures",
        response_type=ResponseType.WEATHER_EMERGENCY,
        character_limit=150
    ),
    "healthcare": KnowledgeCategory(
        name="Healthcare Services",
        priority=Priority.HIGH,
        max_entries=40,
        description="Medical services and health information",
        response_type=ResponseType.MEDICAL_EMERGENCY,
        character_limit=160
    ),
    "utilities": KnowledgeCategory(
        name="Utility Services",
        priority=Priority.HIGH,
        max_entries=25,
        description="Power, water, gas, internet services",
        response_type=ResponseType.UTILITY_EMERGENCY,
        character_limit=160
    ),
    "government": KnowledgeCategory(
        name="Government Services",
        priority=Priority.MEDIUM,
        max_entries=30,
        description="Local government and public services",
        response_type=ResponseType.SERVICE_INFO,
        character_limit=160
    ),
    "transportation": KnowledgeCategory(
        name="Transportation",
        priority=Priority.MEDIUM,
        max_entries=25,
        description="Public transit and road information",
        response_type=ResponseType.TRANSPORTATION_INFO,
        character_limit=160
    ),
    "troubleshooting": KnowledgeCategory(
        name="Troubleshooting",
        priority=Priority.MEDIUM,
        max_entries=35,
        description="Common problem solutions",
        response_type=ResponseType.TECH_SUPPORT,
        character_limit=160
    ),
    "local_info": KnowledgeCategory(
        name="Local Information",
        priority=Priority.LOW,
        max_entries=50,
        description="Local businesses and community info",
        response_type=ResponseType.SERVICE_INFO,
        character_limit=160
    )
}

# Emergency Response Templates
EMERGENCY_RESPONSE_TEMPLATES = {
    "medical_emergency": {
        "template": "EMERGENCY: {action}. Call 911. {steps}. Local ER: {location}. Stay with patient.",
        "max_chars": 140,
        "required_fields": ["action", "steps", "location"]
    },
    "weather_emergency": {
        "template": "WEATHER ALERT: {condition}. {action}. {safety_tips}. Stay informed.",
        "max_chars": 150,
        "required_fields": ["condition", "action", "safety_tips"]
    },
    "utility_emergency": {
        "template": "UTILITY ISSUE: {problem}. {immediate_action}. Call {contact}. {safety_notes}.",
        "max_chars": 160,
        "required_fields": ["problem", "immediate_action", "contact"]
    },
    "general_emergency": {
        "template": "EMERGENCY: Call 911. {situation}. {immediate_steps}. {follow_up}.",
        "max_chars": 140,
        "required_fields": ["situation", "immediate_steps"]
    }
}

# Priority-based storage allocation
STORAGE_ALLOCATION = {
    Priority.CRITICAL: 0.40,  # 40% of storage for critical info
    Priority.HIGH: 0.30,      # 30% for high priority
    Priority.MEDIUM: 0.20,    # 20% for medium priority
    Priority.LOW: 0.10        # 10% for low priority
}

# Response optimization settings
RESPONSE_OPTIMIZATION = {
    "max_sms_length": 160,
    "emergency_max_length": 140,
    "multi_message_threshold": 120,  # Split into multiple messages if longer
    "priority_keywords": [
        "emergency", "urgent", "help", "911", "crisis", "danger",
        "fire", "medical", "police", "ambulance", "hospital"
    ],
    "quick_response_triggers": [
        "emergency", "help", "urgent", "crisis", "danger"
    ]
}

# Offline knowledge base structure
KNOWLEDGE_BASE_STRUCTURE = {
    "emergency": {
        "subcategories": [
            "medical_emergencies",
            "natural_disasters", 
            "safety_procedures",
            "emergency_contacts",
            "evacuation_procedures"
        ],
        "keywords": ["911", "emergency", "urgent", "help", "crisis", "danger"]
    },
    "weather_safety": {
        "subcategories": [
            "severe_weather",
            "heat_safety",
            "cold_safety",
            "storm_procedures",
            "seasonal_preparation"
        ],
        "keywords": ["weather", "storm", "tornado", "flood", "heat", "cold", "snow"]
    },
    "healthcare": {
        "subcategories": [
            "emergency_rooms",
            "urgent_care",
            "pharmacies",
            "mental_health",
            "specialty_care"
        ],
        "keywords": ["hospital", "doctor", "medicine", "pharmacy", "health", "medical"]
    },
    "utilities": {
        "subcategories": [
            "power_outages",
            "water_issues",
            "gas_problems",
            "internet_outages",
            "service_restoration"
        ],
        "keywords": ["power", "electricity", "water", "gas", "internet", "utility"]
    }
}

# Data collection priorities for offline operation
DATA_COLLECTION_PRIORITIES = [
    {
        "category": "emergency",
        "sources": [
            "local_emergency_contacts",
            "emergency_procedures",
            "safety_protocols",
            "evacuation_routes"
        ],
        "update_frequency": "monthly",
        "criticality": "critical"
    },
    {
        "category": "weather_safety",
        "sources": [
            "national_weather_service",
            "local_weather_alerts",
            "seasonal_safety_info",
            "emergency_preparedness"
        ],
        "update_frequency": "daily",
        "criticality": "high"
    },
    {
        "category": "healthcare",
        "sources": [
            "hospital_directories",
            "urgent_care_locations",
            "pharmacy_hours",
            "mental_health_resources"
        ],
        "update_frequency": "weekly",
        "criticality": "high"
    },
    {
        "category": "utilities",
        "sources": [
            "utility_company_contacts",
            "outage_reporting_numbers",
            "service_restoration_info",
            "emergency_procedures"
        ],
        "update_frequency": "monthly",
        "criticality": "high"
    }
]

# SMS response optimization rules
SMS_RESPONSE_RULES = {
    "emergency_response": {
        "max_length": 140,
        "format": "EMERGENCY: [Action]. [Steps]. [Contact]. [Safety].",
        "priority": "immediate"
    },
    "service_response": {
        "max_length": 160,
        "format": "[Service]: [Info]. [Contact]. [Hours]. [Alternative].",
        "priority": "high"
    },
    "information_response": {
        "max_length": 160,
        "format": "[Answer]. [Details]. [Resources]. [Follow-up].",
        "priority": "normal"
    },
    "multi_message": {
        "trigger_length": 120,
        "format": {
            "message_1": "[Topic]: [Brief answer]. More info in next message.",
            "message_2": "[Details]. [Steps]. [Contact info].",
            "message_3": "[Additional info]. [Resources]. [Follow-up]."
        }
    }
}

# Offline operation constraints
OFFLINE_CONSTRAINTS = {
    "max_knowledge_base_size_mb": 100,  # Maximum size for offline storage
    "max_documents_per_category": 1000,  # Maximum documents per category
    "min_response_time_ms": 500,  # Minimum response time for offline queries
    "max_response_time_ms": 2000,  # Maximum response time for offline queries
    "backup_knowledge_sources": [
        "emergency_procedures",
        "basic_contact_info",
        "safety_protocols"
    ],
    "fallback_responses": {
        "unknown_emergency": "Call 911 immediately. Stay safe. Local emergency services are available.",
        "unknown_medical": "For medical emergencies, call 911. For non-emergencies, contact your doctor or visit urgent care.",
        "unknown_service": "Contact your local city hall or visit the city website for more information.",
        "general_help": "For immediate help, call 911. For other assistance, contact your local services or visit the city website."
    }
}

# Knowledge base validation rules
VALIDATION_RULES = {
    "required_fields": ["title", "text", "category", "metadata"],
    "metadata_required": ["priority", "source", "response_type"],
    "text_limits": {
        "min_length": 20,
        "max_length": 1000
    },
    "priority_values": ["critical", "high", "medium", "low"],
    "response_types": [rt.value for rt in ResponseType],
    "category_validation": list(OFFLINE_KNOWLEDGE_CATEGORIES.keys())
}

# Performance optimization settings
PERFORMANCE_SETTINGS = {
    "indexing": {
        "chunk_size": 512,
        "overlap": 50,
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_dimensions": 384
    },
    "search": {
        "similarity_threshold": 0.7,
        "max_results": 5,
        "rerank_results": True,
        "boost_emergency_results": True
    },
    "caching": {
        "enable_response_cache": True,
        "cache_size_mb": 50,
        "cache_ttl_hours": 24,
        "emergency_cache_ttl_hours": 1
    }
}

def get_category_config(category: str) -> Optional[KnowledgeCategory]:
    """Get configuration for a specific category"""
    return OFFLINE_KNOWLEDGE_CATEGORIES.get(category)

def get_emergency_template(response_type: str) -> Dict:
    """Get emergency response template"""
    return EMERGENCY_RESPONSE_TEMPLATES.get(response_type, {})

def validate_knowledge_entry(entry: Dict) -> bool:
    """Validate a knowledge base entry"""
    # Check required fields
    for field in VALIDATION_RULES["required_fields"]:
        if field not in entry:
            return False
    
    # Check metadata
    metadata = entry.get("metadata", {})
    for field in VALIDATION_RULES["metadata_required"]:
        if field not in metadata:
            return False
    
    # Check priority value
    if metadata.get("priority") not in VALIDATION_RULES["priority_values"]:
        return False
    
    # Check category
    if entry.get("category") not in VALIDATION_RULES["category_validation"]:
        return False
    
    # Check text length
    text_length = len(entry.get("text", ""))
    if text_length < VALIDATION_RULES["text_limits"]["min_length"]:
        return False
    if text_length > VALIDATION_RULES["text_limits"]["max_length"]:
        return False
    
    return True

def get_storage_allocation_for_priority(priority: Priority) -> float:
    """Get storage allocation percentage for a priority level"""
    return STORAGE_ALLOCATION.get(priority, 0.0)

def get_response_optimization_config() -> Dict:
    """Get response optimization configuration"""
    return RESPONSE_OPTIMIZATION

def get_offline_constraints() -> Dict:
    """Get offline operation constraints"""
    return OFFLINE_CONSTRAINTS
