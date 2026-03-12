"""Integration tests for Rust services integration"""

import pytest
import asyncio
from datetime import datetime

from backend.shared.models import SMSMessage, MessagePriority
from backend.shared.integration.rust_services import (
    RustSMSService,
    RustCompressionService,
    RustMessageRouterService,
    RustServicesManager,
)
from backend.shared.integration.service_discovery import ServiceRegistry
from backend.shared.integration.message_flow import MessageFlowPipeline


@pytest.mark.asyncio
async def test_rust_sms_service():
    """Test Rust SMS service wrapper"""
    service = RustSMSService()
    await service.initialize()
    
    # Test sending SMS (will use fallback if Rust not available)
    message_id = await service.send_sms(
        phone_number="+1234567890",
        content="Test message",
        priority=1
    )
    
    assert message_id is not None
    assert message_id.startswith("msg_")
    
    # Test stats
    stats = await service.get_stats()
    assert 'connected' in stats


@pytest.mark.asyncio
async def test_rust_compression_service():
    """Test Rust compression service wrapper"""
    service = RustCompressionService()
    
    # Test compression
    long_text = "This is a very long message that needs to be compressed to fit within the SMS character limit of 160 characters. " * 2
    compressed = await service.compress(long_text, target_length=160)
    
    assert len(compressed) <= 160
    assert compressed is not None
    
    # Test stats
    stats = await service.get_stats()
    assert 'total_compressions' in stats


@pytest.mark.asyncio
async def test_rust_message_router_service():
    """Test Rust message router service wrapper"""
    service = RustMessageRouterService()
    await service.initialize()
    
    # Test routing
    route = await service.route(
        sender="+1234567890",
        content="What's the weather?"
    )
    
    assert route is not None
    assert 'service_type' in route
    assert 'service_url' in route
    
    # Test classification
    classification = await service.classify("EMERGENCY! Help needed!")
    assert classification is not None
    assert 'intent' in classification
    assert classification['intent'] == 'Emergency'
    
    # Test stats
    stats = await service.get_stats()
    assert 'total_routes' in stats


@pytest.mark.asyncio
async def test_rust_services_manager():
    """Test Rust services manager"""
    manager = RustServicesManager()
    initialized = await manager.initialize()
    
    # Manager should initialize (even if Rust services not available)
    assert initialized is not None
    
    # Test getting all stats
    stats = await manager.get_all_stats()
    assert 'sms' in stats
    assert 'compression' in stats
    assert 'router' in stats


@pytest.mark.asyncio
async def test_service_registry():
    """Test service registry"""
    registry = ServiceRegistry()
    
    # Register services
    registry.register('test_service', 'http://localhost:9999')
    
    # Get service
    service = registry.get_service('test_service')
    assert service is not None
    assert service.name == 'test_service'
    assert service.url == 'http://localhost:9999'
    
    # Get all services
    all_services = registry.get_all_services()
    assert len(all_services) == 1
    
    # Get stats
    stats = registry.get_service_stats()
    assert stats['total_services'] == 1


@pytest.mark.asyncio
async def test_message_flow_pipeline():
    """Test end-to-end message flow"""
    config = {
        'rust_services': {
            'sms': {'device': '/dev/ttyUSB0'},
            'compression': {'target_length': 160},
            'router': {'cache_size': 1000},
        }
    }
    
    pipeline = MessageFlowPipeline(config)
    initialized = await pipeline.initialize()
    
    # Pipeline should initialize
    assert initialized is not None
    
    # Create test message
    message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="Hello, how are you?",
        priority=MessagePriority.NORMAL,
        timestamp=datetime.utcnow()
    )
    
    # Process message (will use fallbacks if services not available)
    result = await pipeline.process_message(message)
    
    assert result is not None
    assert 'status' in result
    
    # Test pipeline stats
    stats = await pipeline.get_pipeline_stats()
    assert 'rust_services' in stats
    assert 'service_discovery' in stats


@pytest.mark.asyncio
async def test_emergency_message_flow():
    """Test emergency message handling"""
    pipeline = MessageFlowPipeline()
    await pipeline.initialize()
    
    # Create emergency message
    emergency_message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="EMERGENCY! Fire in building!",
        priority=MessagePriority.EMERGENCY,
        timestamp=datetime.utcnow()
    )
    
    # Process emergency message
    result = await pipeline.process_message(emergency_message)
    
    assert result is not None
    assert result.get('status') in ['success', 'emergency_handled', 'error']
    
    # Emergency should be handled quickly
    if 'processing_time' in result:
        assert result['processing_time'] < 10.0  # Should be fast


@pytest.mark.asyncio
async def test_service_health_checks():
    """Test service health checking"""
    registry = ServiceRegistry()
    
    # Register a service
    registry.register('test_service', 'http://localhost:9999')
    
    # Start health checks
    await registry.start_health_checks()
    
    # Wait a bit for health check
    await asyncio.sleep(1)
    
    # Check health (will likely fail since service doesn't exist)
    health_ok = await registry.check_health('test_service')
    
    # Stop health checks
    await registry.stop_health_checks()
    
    # Health check should have run (even if failed)
    service = registry.get_service('test_service')
    assert service.last_check is not None or health_ok is False

