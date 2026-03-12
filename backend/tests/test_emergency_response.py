"""Tests for Emergency Response Service"""

import pytest
from datetime import datetime

from backend.shared.models import SMSMessage, MessagePriority
from backend.services.emergency_response.service import EmergencyResponseService
from backend.services.emergency_response.detector import EmergencyDetector, EmergencyType, EmergencySeverity
from backend.services.emergency_response.templates import EmergencyTemplates


def test_emergency_detection():
    """Test emergency detection"""
    detector = EmergencyDetector()
    
    # Test medical emergency
    detection = detector.detect("My dad is having a heart attack!")
    assert detection.is_emergency
    assert detection.emergency_type == EmergencyType.MEDICAL
    assert detection.severity == EmergencySeverity.CRITICAL
    assert detection.confidence > 0.9
    
    # Test fire emergency
    detection = detector.detect("There's a fire in the building!")
    assert detection.is_emergency
    assert detection.emergency_type == EmergencyType.FIRE
    assert detection.severity == EmergencySeverity.CRITICAL
    
    # Test natural disaster
    detection = detector.detect("Tornado warning! What should I do?")
    assert detection.is_emergency
    assert detection.emergency_type == EmergencyType.NATURAL_DISASTER
    
    # Test non-emergency
    detection = detector.detect("What's the weather today?")
    assert not detection.is_emergency


def test_critical_emergency_check():
    """Test critical emergency quick check"""
    detector = EmergencyDetector()
    
    assert detector.is_critical_emergency("Heart attack! Help!")
    assert detector.is_critical_emergency("Fire! Building burning!")
    assert not detector.is_critical_emergency("What's the weather?")


def test_emergency_templates():
    """Test emergency templates"""
    templates = EmergencyTemplates()
    
    # Test medical template
    template = templates.get_template(EmergencyType.MEDICAL, severity='critical')
    assert template is not None
    assert len(template) > 0
    assert '911' in template or 'CALL' in template
    
    # Test fire template
    template = templates.get_template(EmergencyType.FIRE, severity='critical')
    assert template is not None
    assert 'FIRE' in template or 'fire' in template
    
    # Test disaster protocol
    protocol = templates.get_disaster_protocol('tornado')
    assert protocol is not None
    assert 'TORNADO' in protocol or 'tornado' in protocol


def test_emergency_contacts():
    """Test emergency contacts"""
    templates = EmergencyTemplates()
    contacts = templates.get_emergency_contacts()
    
    assert '911' in contacts
    assert 'poison_control' in contacts
    assert contacts['911'] == '911'


@pytest.mark.asyncio
async def test_emergency_response_service():
    """Test emergency response service"""
    service = EmergencyResponseService()
    
    # Test medical emergency
    message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="EMERGENCY! My dad is having chest pain!",
        priority=MessagePriority.EMERGENCY,
        timestamp=datetime.utcnow()
    )
    
    result = await service.handle_emergency(message)
    
    assert result is not None
    assert result['is_emergency']
    assert result['emergency_type'] == EmergencyType.MEDICAL.value
    assert result['severity'] == EmergencySeverity.CRITICAL.value
    assert 'response_text' in result
    assert len(result['response_text']) <= 160  # SMS limit
    assert result['response_time_ms'] < 100  # Should be fast (<100ms)


@pytest.mark.asyncio
async def test_emergency_response_fire():
    """Test fire emergency response"""
    service = EmergencyResponseService()
    
    message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="FIRE! Building is on fire!",
        priority=MessagePriority.EMERGENCY,
        timestamp=datetime.utcnow()
    )
    
    result = await service.handle_emergency(message)
    
    assert result is not None
    assert result['emergency_type'] == EmergencyType.FIRE.value
    assert 'FIRE' in result['response_text'] or 'fire' in result['response_text']


@pytest.mark.asyncio
async def test_emergency_response_tornado():
    """Test tornado emergency response"""
    service = EmergencyResponseService()
    
    message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="Tornado warning! What should I do?",
        priority=MessagePriority.EMERGENCY,
        timestamp=datetime.utcnow()
    )
    
    result = await service.handle_emergency(message)
    
    assert result is not None
    assert result['emergency_type'] == EmergencyType.NATURAL_DISASTER.value
    assert 'TORNADO' in result['response_text'] or 'tornado' in result['response_text']


@pytest.mark.asyncio
async def test_non_emergency():
    """Test non-emergency message"""
    service = EmergencyResponseService()
    
    message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="What's the weather today?",
        priority=MessagePriority.NORMAL,
        timestamp=datetime.utcnow()
    )
    
    result = await service.handle_emergency(message)
    
    assert result is None  # Not an emergency


@pytest.mark.asyncio
async def test_resource_aware_compression():
    """Test resource-aware compression for emergencies"""
    service = EmergencyResponseService()
    
    # Set low battery
    service.update_resources(battery_level=15, memory_mb=200)
    
    message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="EMERGENCY! Help needed!",
        priority=MessagePriority.EMERGENCY,
        timestamp=datetime.utcnow()
    )
    
    result = await service.handle_emergency(message)
    
    assert result is not None
    # Should use truncation instead of compression when battery <20%
    assert len(result['response_text']) <= 160


def test_emergency_statistics():
    """Test emergency statistics"""
    service = EmergencyResponseService()
    
    stats = service.get_statistics()
    
    assert 'total_emergencies' in stats
    assert 'critical_emergencies' in stats
    assert 'medical_emergencies' in stats
    assert 'fire_emergencies' in stats
    assert 'average_response_time_ms' in stats


def test_local_contacts():
    """Test local emergency contacts"""
    service = EmergencyResponseService()
    
    # Add local contact
    service.add_local_contact('local_police', '555-1234')
    
    # Verify contact added
    contacts = service.contacts_db.get_all_contacts()
    assert 'local_police' in contacts
    assert contacts['local_police'] == '555-1234'

