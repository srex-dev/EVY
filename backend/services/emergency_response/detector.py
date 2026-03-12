"""Emergency Detection Module

Fast pattern-based emergency detection optimized for edge deployment.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Emergency type enumeration"""
    MEDICAL = "medical"
    FIRE = "fire"
    POLICE = "police"
    NATURAL_DISASTER = "natural_disaster"
    GENERAL = "general"
    NONE = "none"


class EmergencySeverity(Enum):
    """Emergency severity levels"""
    CRITICAL = "critical"  # Life-threatening
    HIGH = "high"         # Urgent but not immediately life-threatening
    MEDIUM = "medium"     # Important but can wait
    LOW = "low"          # Informational


@dataclass
class EmergencyDetection:
    """Emergency detection result"""
    is_emergency: bool
    emergency_type: EmergencyType
    severity: EmergencySeverity
    confidence: float  # 0.0-1.0
    keywords_found: List[str]
    location_hints: Optional[str] = None


class EmergencyDetector:
    """Fast pattern-based emergency detector"""
    
    def __init__(self):
        # Pre-compiled regex patterns for fast matching
        self.patterns = self._compile_patterns()
        
        # Emergency keywords by type
        self.keywords = {
            EmergencyType.MEDICAL: {
                'critical': ['heart attack', 'stroke', 'chest pain', 'can\'t breathe', 'choking', 'unconscious', 'not breathing', 'seizure', 'bleeding heavily'],
                'high': ['medical', 'hospital', 'ambulance', 'doctor', 'emergency room', 'injured', 'pain', 'sick', 'illness'],
                'medium': ['medicine', 'prescription', 'symptoms', 'fever', 'headache'],
            },
            EmergencyType.FIRE: {
                'critical': ['fire', 'burning', 'smoke', 'flames', 'explosion'],
                'high': ['smoke alarm', 'fire alarm', 'evacuate', 'evacuation'],
                'medium': ['smell smoke', 'hot', 'burning smell'],
            },
            EmergencyType.POLICE: {
                'critical': ['help', 'danger', 'threat', 'weapon', 'attack', 'assault', 'robbery'],
                'high': ['police', '911', 'emergency', 'urgent', 'dangerous'],
                'medium': ['suspicious', 'stranger', 'concerned'],
            },
            EmergencyType.NATURAL_DISASTER: {
                'critical': ['tornado', 'hurricane', 'earthquake', 'flood', 'tsunami'],
                'high': ['storm', 'warning', 'alert', 'evacuate', 'shelter'],
                'medium': ['weather', 'severe weather', 'precipitation'],
            },
        }
    
    def _compile_patterns(self) -> Dict[EmergencyType, List[re.Pattern]]:
        """Compile regex patterns for emergency detection"""
        patterns = {}
        
        # Medical patterns
        patterns[EmergencyType.MEDICAL] = [
            re.compile(r'\b(heart\s*attack|stroke|chest\s*pain|can\'t\s*breathe|choking|unconscious|not\s*breathing|seizure|bleeding\s*heavily)\b', re.IGNORECASE),
            re.compile(r'\b(medical|hospital|ambulance|doctor|emergency\s*room|injured)\b', re.IGNORECASE),
        ]
        
        # Fire patterns
        patterns[EmergencyType.FIRE] = [
            re.compile(r'\b(fire|burning|smoke|flames|explosion)\b', re.IGNORECASE),
            re.compile(r'\b(fire\s*alarm|smoke\s*alarm|evacuate|evacuation)\b', re.IGNORECASE),
        ]
        
        # Police patterns
        patterns[EmergencyType.POLICE] = [
            re.compile(r'\b(help|danger|threat|weapon|attack|assault|robbery)\b', re.IGNORECASE),
            re.compile(r'\b(police|911|emergency|urgent|dangerous)\b', re.IGNORECASE),
        ]
        
        # Natural disaster patterns
        patterns[EmergencyType.NATURAL_DISASTER] = [
            re.compile(r'\b(tornado|hurricane|earthquake|flood|tsunami)\b', re.IGNORECASE),
            re.compile(r'\b(storm|warning|alert|evacuate|shelter)\b', re.IGNORECASE),
        ]
        
        return patterns
    
    def detect(self, text: str) -> EmergencyDetection:
        """Detect emergency in text"""
        text_lower = text.lower()
        found_keywords = []
        emergency_type = EmergencyType.NONE
        severity = EmergencySeverity.LOW
        confidence = 0.0
        
        # Check each emergency type
        for etype, type_patterns in self.patterns.items():
            for pattern in type_patterns:
                matches = pattern.findall(text_lower)
                if matches:
                    found_keywords.extend(matches)
                    
                    # Determine severity based on keywords
                    if etype == EmergencyType.MEDICAL:
                        if any(kw in text_lower for kw in ['heart attack', 'stroke', 'chest pain', 'can\'t breathe', 'choking']):
                            severity = EmergencySeverity.CRITICAL
                            confidence = 0.95
                        else:
                            severity = EmergencySeverity.HIGH
                            confidence = 0.85
                    elif etype == EmergencyType.FIRE:
                        if any(kw in text_lower for kw in ['fire', 'burning', 'smoke', 'flames']):
                            severity = EmergencySeverity.CRITICAL
                            confidence = 0.95
                        else:
                            severity = EmergencySeverity.HIGH
                            confidence = 0.85
                    elif etype == EmergencyType.POLICE:
                        if any(kw in text_lower for kw in ['help', 'danger', 'threat', 'weapon', 'attack']):
                            severity = EmergencySeverity.CRITICAL
                            confidence = 0.90
                        else:
                            severity = EmergencySeverity.HIGH
                            confidence = 0.80
                    elif etype == EmergencyType.NATURAL_DISASTER:
                        if any(kw in text_lower for kw in ['tornado', 'hurricane', 'earthquake', 'flood']):
                            severity = EmergencySeverity.CRITICAL
                            confidence = 0.90
                        else:
                            severity = EmergencySeverity.HIGH
                            confidence = 0.80
                    
                    emergency_type = etype
                    break
            
            if emergency_type != EmergencyType.NONE:
                break
        
        # Check for general emergency keywords if no specific type found
        if emergency_type == EmergencyType.NONE:
            general_keywords = ['emergency', 'help', 'urgent', '911', 'sos']
            if any(kw in text_lower for kw in general_keywords):
                emergency_type = EmergencyType.GENERAL
                severity = EmergencySeverity.HIGH
                confidence = 0.70
                found_keywords = [kw for kw in general_keywords if kw in text_lower]
        
        is_emergency = emergency_type != EmergencyType.NONE
        
        # Extract location hints if present
        location_hints = self._extract_location(text)
        
        return EmergencyDetection(
            is_emergency=is_emergency,
            emergency_type=emergency_type,
            severity=severity,
            confidence=confidence,
            keywords_found=found_keywords,
            location_hints=location_hints,
        )
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location hints from text"""
        # Simple location extraction (can be enhanced)
        location_patterns = [
            r'\b(at|in|near|on)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "at Main Street"
            r'\b([0-9]+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd))',  # "123 Main Street"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def is_critical_emergency(self, text: str) -> bool:
        """Quick check if message is a critical emergency"""
        detection = self.detect(text)
        return detection.is_emergency and detection.severity == EmergencySeverity.CRITICAL

