"""Emergency Response Service

Provides emergency detection, response templates, and disaster-specific protocols.
"""

from backend.services.emergency_response.service import EmergencyResponseService
from backend.services.emergency_response.templates import EmergencyTemplates
from backend.services.emergency_response.detector import EmergencyDetector

__all__ = [
    'EmergencyResponseService',
    'EmergencyTemplates',
    'EmergencyDetector',
]

