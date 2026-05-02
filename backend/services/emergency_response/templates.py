"""Emergency Response Templates

Pre-loaded emergency response templates optimized for edge deployment.
All templates are in-memory for fast access (<10ms lookup).
"""

from typing import Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Emergency type enumeration"""
    MEDICAL = "medical"
    FIRE = "fire"
    POLICE = "police"
    NATURAL_DISASTER = "natural_disaster"
    GENERAL = "general"


class EmergencyTemplates:
    """Pre-loaded emergency response templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
        logger.info(f"Loaded {len(self.templates)} emergency templates")
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load emergency response templates"""
        return {
            EmergencyType.MEDICAL.value: {
                'critical': (
                    "CALL 911 IMMEDIATELY. Keep person calm, seated, loosen clothing. "
                    "If heart medication available, help take it. DO NOT drive - wait for ambulance. "
                    "Stay with person. Local ER: Check local directory."
                ),
                'high': (
                    "Medical emergency received. Call 911 or go to nearest emergency room. "
                    "Stay with person if safe. Describe symptoms clearly to dispatcher."
                ),
                'general': (
                    "Medical assistance needed. Call 911 for emergencies or visit urgent care for non-emergencies. "
                    "Stay calm and follow dispatcher instructions."
                ),
            },
            EmergencyType.FIRE.value: {
                'critical': (
                    "FIRE EMERGENCY: Call 911 immediately. Evacuate immediately if safe. "
                    "Do NOT use elevator. Stay low if smoke present. Meet at designated safe location."
                ),
                'high': (
                    "Fire emergency received. Call 911. Evacuate building immediately. "
                    "Do not re-enter until cleared by fire department."
                ),
                'general': (
                    "Fire safety: Call 911 if fire present. Evacuate immediately. "
                    "Use stairs, not elevators. Meet at safe location."
                ),
            },
            EmergencyType.POLICE.value: {
                'critical': (
                    "CALL 911 IMMEDIATELY. If safe, move to secure location. "
                    "Do not approach threat. Provide location and description to dispatcher. "
                    "Stay on line until help arrives."
                ),
                'high': (
                    "Police emergency received. Call 911 immediately. "
                    "Provide location and details. Stay safe and follow dispatcher instructions."
                ),
                'general': (
                    "Emergency assistance needed. Call 911 for immediate help. "
                    "Provide clear location and situation details."
                ),
            },
            EmergencyType.NATURAL_DISASTER.value: {
                'tornado': (
                    "TORNADO WARNING: Go to lowest floor, interior room, away from windows. "
                    "Cover head and neck. Avoid mobile homes. Stay in shelter until all clear."
                ),
                'hurricane': (
                    "HURRICANE: Evacuate if ordered. If staying, go to interior room on lowest floor. "
                    "Stay away from windows. Monitor weather updates."
                ),
                'earthquake': (
                    "EARTHQUAKE: Drop, cover, hold on. Stay away from windows and heavy objects. "
                    "If outside, move to open area away from buildings."
                ),
                'flood': (
                    "FLOOD WARNING: Move to higher ground immediately. Do not drive through flooded areas. "
                    "Avoid walking through floodwaters. Evacuate if ordered."
                ),
                'general': (
                    "Natural disaster alert. Follow local emergency instructions. "
                    "Evacuate if ordered. Go to designated shelter if needed."
                ),
            },
            EmergencyType.GENERAL.value: {
                'default': (
                    "Emergency alert received. Call 911 for immediate assistance. "
                    "Stay calm. Provide location and details to dispatcher. Help is on the way."
                ),
            },
        }
    
    def get_template(
        self,
        emergency_type: EmergencyType,
        severity: str = 'general',
        disaster_subtype: Optional[str] = None
    ) -> str:
        """Get emergency response template"""
        type_key = emergency_type.value
        
        if type_key not in self.templates:
            return self.templates[EmergencyType.GENERAL.value]['default']
        
        type_templates = self.templates[type_key]
        
        # For natural disasters, check for specific subtype. The detector and
        # template modules define separate EmergencyType enums, so compare by
        # value rather than enum identity.
        if type_key == EmergencyType.NATURAL_DISASTER.value and disaster_subtype:
            if disaster_subtype in type_templates:
                return type_templates[disaster_subtype]
        
        # Try severity-specific template
        if severity in type_templates:
            return type_templates[severity]
        
        # Fallback to general
        if 'general' in type_templates:
            return type_templates['general']
        
        # Final fallback
        return self.templates[EmergencyType.GENERAL.value]['default']
    
    def get_emergency_contacts(self) -> Dict[str, str]:
        """Get emergency contact numbers"""
        return {
            '911': '911',
            'poison_control': '1-800-222-1222',
            'suicide_prevention': '988',
            'disaster_relief': '1-800-RED-CROSS',
        }
    
    def get_disaster_protocol(self, disaster_type: str) -> Optional[str]:
        """Get disaster-specific protocol"""
        protocols = {
            'tornado': self.templates[EmergencyType.NATURAL_DISASTER.value].get('tornado'),
            'hurricane': self.templates[EmergencyType.NATURAL_DISASTER.value].get('hurricane'),
            'earthquake': self.templates[EmergencyType.NATURAL_DISASTER.value].get('earthquake'),
            'flood': self.templates[EmergencyType.NATURAL_DISASTER.value].get('flood'),
        }
        return protocols.get(disaster_type.lower())

