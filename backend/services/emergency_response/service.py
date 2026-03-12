"""Emergency Response Service

Main service for handling emergency messages with resource-aware processing.
"""

import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
import logging

from backend.shared.models import SMSMessage, MessagePriority
from backend.services.emergency_response.detector import (
    EmergencyDetector,
    EmergencyType,
    EmergencySeverity,
    EmergencyDetection,
)
from backend.services.emergency_response.templates import EmergencyTemplates
from backend.shared.integration.rust_services import RustCompressionService

logger = logging.getLogger(__name__)


class EmergencyContactsDB:
    """Simple in-memory emergency contacts database"""
    
    def __init__(self):
        self.contacts = {
            '911': '911',
            'police': '911',
            'fire': '911',
            'ambulance': '911',
            'poison_control': '1-800-222-1222',
            'suicide_prevention': '988',
            'disaster_relief': '1-800-RED-CROSS',
            'fema': '1-800-621-FEMA',
        }
        
        # Local emergency contacts (can be configured)
        self.local_contacts = {}
    
    def get_contact(self, contact_type: str) -> Optional[str]:
        """Get emergency contact number"""
        return self.contacts.get(contact_type.lower()) or self.local_contacts.get(contact_type.lower())
    
    def add_local_contact(self, contact_type: str, number: str) -> None:
        """Add local emergency contact"""
        self.local_contacts[contact_type.lower()] = number
        logger.info(f"Added local contact: {contact_type} -> {number}")
    
    def get_all_contacts(self) -> Dict[str, str]:
        """Get all emergency contacts"""
        return {**self.contacts, **self.local_contacts}


class EmergencyResponseService:
    """Emergency response service with resource-aware processing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.detector = EmergencyDetector()
        self.templates = EmergencyTemplates()
        self.contacts_db = EmergencyContactsDB()
        
        # Compression service (resource-aware)
        compression_config = self.config.get('compression', {})
        compression_config['battery_threshold'] = 20  # Lower threshold for emergencies
        self.compression_service = RustCompressionService(compression_config)
        
        # Resource monitoring (would integrate with actual monitoring)
        self.battery_level = 100  # Default: full battery
        self.memory_mb = 1000  # Default: 1GB available
        
        # Statistics
        self.stats = {
            'total_emergencies': 0,
            'critical_emergencies': 0,
            'medical_emergencies': 0,
            'fire_emergencies': 0,
            'police_emergencies': 0,
            'natural_disaster_emergencies': 0,
            'average_response_time_ms': 0.0,
        }
    
    def update_resources(self, battery_level: int, memory_mb: int) -> None:
        """Update resource levels"""
        self.battery_level = battery_level
        self.memory_mb = memory_mb
        logger.debug(f"Resources updated: battery={battery_level}%, memory={memory_mb}MB")
    
    async def handle_emergency(
        self,
        message: SMSMessage
    ) -> Optional[Dict[str, Any]]:
        """Handle emergency message with fast response"""
        start_time = datetime.utcnow()
        
        # Detect emergency (fast pattern matching)
        detection = self.detector.detect(message.content)
        
        if not detection.is_emergency:
            return None
        
        logger.critical(
            f"EMERGENCY DETECTED: Type={detection.emergency_type.value}, "
            f"Severity={detection.severity.value}, Confidence={detection.confidence:.2f}, "
            f"From={message.sender}, Content={message.content[:100]}"
        )
        
        # Update statistics
        self.stats['total_emergencies'] += 1
        if detection.severity == EmergencySeverity.CRITICAL:
            self.stats['critical_emergencies'] += 1
        
        # Track by type
        if detection.emergency_type == EmergencyType.MEDICAL:
            self.stats['medical_emergencies'] += 1
        elif detection.emergency_type == EmergencyType.FIRE:
            self.stats['fire_emergencies'] += 1
        elif detection.emergency_type == EmergencyType.POLICE:
            self.stats['police_emergencies'] += 1
        elif detection.emergency_type == EmergencyType.NATURAL_DISASTER:
            self.stats['natural_disaster_emergencies'] += 1
        
        # Get emergency response template
        severity_str = detection.severity.value
        disaster_subtype = None
        
        # Extract disaster subtype for natural disasters
        if detection.emergency_type == EmergencyType.NATURAL_DISASTER:
            text_lower = message.content.lower()
            if 'tornado' in text_lower:
                disaster_subtype = 'tornado'
            elif 'hurricane' in text_lower:
                disaster_subtype = 'hurricane'
            elif 'earthquake' in text_lower:
                disaster_subtype = 'earthquake'
            elif 'flood' in text_lower:
                disaster_subtype = 'flood'
        
        response_text = self.templates.get_template(
            detection.emergency_type,
            severity=severity_str,
            disaster_subtype=disaster_subtype
        )
        
        # Add emergency contact if relevant
        if detection.emergency_type == EmergencyType.MEDICAL:
            contact = self.contacts_db.get_contact('ambulance')
            if contact:
                response_text += f" Emergency: {contact}"
        elif detection.emergency_type == EmergencyType.FIRE:
            contact = self.contacts_db.get_contact('fire')
            if contact:
                response_text += f" Fire: {contact}"
        elif detection.emergency_type == EmergencyType.POLICE:
            contact = self.contacts_db.get_contact('police')
            if contact:
                response_text += f" Police: {contact}"
        
        # Compress response if needed (resource-aware)
        if len(response_text) > 160:
            # Only compress if battery >20% (edge optimization)
            if self.battery_level > 20:
                try:
                    response_text = await self.compression_service.compress(
                        response_text,
                        target_length=160
                    )
                    logger.debug("Emergency response compressed")
                except Exception as e:
                    logger.warning(f"Compression failed, truncating: {e}")
                    response_text = response_text[:157] + "..."
            else:
                # Low battery: simple truncation (faster)
                response_text = response_text[:157] + "..."
                logger.debug("Low battery, using truncation instead of compression")
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Update average response time
        n = self.stats['total_emergencies']
        self.stats['average_response_time_ms'] = (
            (self.stats['average_response_time_ms'] * (n - 1) + response_time) / n
        )
        
        return {
            'is_emergency': True,
            'emergency_type': detection.emergency_type.value,
            'severity': detection.severity.value,
            'confidence': detection.confidence,
            'response_text': response_text,
            'response_time_ms': response_time,
            'keywords_found': detection.keywords_found,
            'location_hints': detection.location_hints,
            'priority': MessagePriority.EMERGENCY,
        }
    
    def is_emergency(self, text: str) -> bool:
        """Quick check if text contains emergency"""
        return self.detector.detect(text).is_emergency
    
    def is_critical_emergency(self, text: str) -> bool:
        """Quick check if text is critical emergency"""
        return self.detector.is_critical_emergency(text)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get emergency response statistics"""
        return {
            **self.stats,
            'battery_level': self.battery_level,
            'memory_mb': self.memory_mb,
        }
    
    def add_local_contact(self, contact_type: str, number: str) -> None:
        """Add local emergency contact"""
        self.contacts_db.add_local_contact(contact_type, number)

