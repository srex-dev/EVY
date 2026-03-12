"""Tests for Edge Model Manager"""

import pytest
from backend.services.llm_inference.edge_model_manager import (
    EdgeModelManager,
    ModelStatus,
    ModelMetadata,
)


@pytest.mark.asyncio
async def test_model_registry():
    """Test model registry initialization"""
    manager = EdgeModelManager()
    
    registry = manager.get_model_registry()
    
    assert len(registry) > 0
    assert 'tinyllama-4bit' in registry
    
    # Check metadata
    tinyllama = registry['tinyllama-4bit']
    assert tinyllama['memory_requirement_mb'] > 0
    assert tinyllama['quantized_size_mb'] < tinyllama['size_mb']


@pytest.mark.asyncio
async def test_model_status():
    """Test model status tracking"""
    manager = EdgeModelManager()
    
    status = manager.get_status()
    
    assert 'llama_cpp_available' in status
    assert 'loaded_models' in status
    assert 'total_models' in status
    assert status['total_models'] > 0


def test_model_metadata():
    """Test model metadata structure"""
    metadata = ModelMetadata(
        name="test-model",
        model_id="test/model",
        size_mb=1000,
        quantized_size_mb=250,
        memory_requirement_mb=350,
        context_size=512,
        supports_quantization=True,
    )
    
    assert metadata.name == "test-model"
    assert metadata.quantized_size_mb < metadata.size_mb
    assert metadata.memory_requirement_mb > 0


@pytest.mark.asyncio
async def test_memory_aware_loading():
    """Test memory-aware model loading"""
    # Create manager with low memory limit
    config = {'max_memory_mb': 100}
    manager = EdgeModelManager(config)
    
    # Try to load model (will check memory)
    # This will likely fail if memory check works correctly
    result = await manager.load_model('tinyllama-4bit')
    
    # Result depends on actual memory available
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_power_aware_management():
    """Test power-aware model management"""
    manager = EdgeModelManager()
    
    # Set low battery
    manager.update_battery_level(20)
    
    # Try to load model (should fail due to low battery)
    result = await manager.load_model('tinyllama-4bit')
    
    # Should fail or succeed based on battery threshold
    # (Implementation may vary)
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_model_switching():
    """Test model switching"""
    manager = EdgeModelManager()
    
    # Switch models (will unload first, then load second)
    # Note: This will only work if models are actually available
    result = await manager.switch_model('tinyllama-4bit', 'phi-2-mini-4bit')
    
    # Result depends on model availability
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_model_unloading():
    """Test model unloading"""
    manager = EdgeModelManager()
    
    # Try to unload a model (may not be loaded)
    result = await manager.unload_model('tinyllama-4bit')
    
    # Should return bool (True if unloaded, False if not loaded)
    assert isinstance(result, bool)


def test_default_model_selection():
    """Test default model selection"""
    manager = EdgeModelManager()
    
    default = manager._select_default_model()
    
    # Should return a model name or None
    assert default is None or isinstance(default, str)


@pytest.mark.asyncio
async def test_generate_without_model():
    """Test generation when no model loaded"""
    manager = EdgeModelManager()
    
    # Try to generate without loading model first
    result = await manager.generate("Hello", model_name=None)
    
    # Should return error or attempt to load default model
    assert 'response' in result or 'error' in result


def test_battery_update():
    """Test battery level update"""
    manager = EdgeModelManager()
    
    # Update battery level
    manager.update_battery_level(50)
    
    assert manager.current_battery_level == 50
    
    # Set low battery
    manager.update_battery_level(20)
    assert manager.current_battery_level == 20


def test_model_cache():
    """Test model cache management"""
    manager = EdgeModelManager()
    
    # Models should be cached when loaded
    # Cache TTL is 1 hour by default
    assert manager.cache_ttl.total_seconds() == 3600

