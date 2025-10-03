"""Pytest configuration and fixtures for EVY tests."""
import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.sms_gateway.main import app as sms_app, sms_gateway
from backend.services.llm_inference.main import app as llm_app, llm_engine
from backend.services.message_router.main import app as router_app
from backend.shared.models import SMSMessage, MessagePriority


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sms_client():
    """SMS Gateway test client."""
    return TestClient(sms_app)


@pytest.fixture
def llm_client():
    """LLM Inference test client."""
    return TestClient(llm_app)


@pytest.fixture
def router_client():
    """Message Router test client."""
    return TestClient(router_app)


@pytest.fixture
def sample_sms_message():
    """Sample SMS message for testing."""
    return SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="Hello, this is a test message",
        priority=MessagePriority.NORMAL
    )


@pytest.fixture
def sample_emergency_message():
    """Sample emergency SMS message for testing."""
    return SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="Emergency! Need help immediately!",
        priority=MessagePriority.EMERGENCY
    )


@pytest.fixture
def mock_gsm_driver():
    """Mock GSM driver for testing."""
    mock_driver = Mock()
    mock_driver.initialize = AsyncMock(return_value=True)
    mock_driver.send_sms = AsyncMock(return_value=True)
    mock_driver.receive_sms = AsyncMock(return_value=[])
    mock_driver.disconnect = AsyncMock()
    mock_driver.health_check = AsyncMock(return_value={
        "connected": True,
        "signal_strength": 85,
        "network_name": "Test Network"
    })
    return mock_driver


@pytest.fixture
def mock_message_queue():
    """Mock message queue for testing."""
    mock_queue = Mock()
    mock_queue.initialize = AsyncMock(return_value=True)
    mock_queue.enqueue_message = AsyncMock(return_value="test_message_id")
    mock_queue.dequeue_message = AsyncMock(return_value=None)
    mock_queue.mark_sent = AsyncMock()
    mock_queue.mark_failed = AsyncMock()
    mock_queue.get_queue_stats = AsyncMock(return_value={
        "pending": 0,
        "processing": 0,
        "sent": 0,
        "failed": 0,
        "total_messages": 0
    })
    return mock_queue


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "response": "This is a test response from the LLM.",
        "model_used": "test-model",
        "tokens_used": 15,
        "processing_time": 1.5,
        "metadata": {}
    }


@pytest.fixture
async def http_client():
    """HTTP client for integration tests."""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis for tests that don't need real Redis."""
    import redis
    mock_redis = Mock()
    mock_redis.ping = Mock(return_value=True)
    mock_redis.hset = Mock()
    mock_redis.zadd = Mock()
    mock_redis.zrem = Mock()
    mock_redis.zrangebyscore = Mock(return_value=[])
    mock_redis.hgetall = Mock(return_value={})
    mock_redis.zcard = Mock(return_value=0)
    mock_redis.delete = Mock()
    mock_redis.expire = Mock()
    mock_redis.bzpopmin = Mock(return_value=None)
    mock_redis.zscore = Mock(return_value=None)
    
    # Patch redis.from_url
    original_from_url = redis.from_url
    redis.from_url = Mock(return_value=mock_redis)
    
    yield mock_redis
    
    # Restore original function
    redis.from_url = original_from_url


@pytest.fixture(autouse=True)
def mock_gammu():
    """Mock Gammu library for tests."""
    try:
        import gammu
        mock_state_machine = Mock()
        mock_state_machine.ReadConfig = Mock()
        mock_state_machine.Init = Mock()
        mock_state_machine.SendSMS = Mock()
        mock_state_machine.GetSMSFoldersStatus = Mock(return_value=[])
        mock_state_machine.GetNextSMS = Mock(side_effect=Exception("No more messages"))
        mock_state_machine.DeleteSMS = Mock()
        mock_state_machine.GetSignalQuality = Mock(return_value={"SignalPercent": 85})
        mock_state_machine.GetNetworkInfo = Mock(return_value={"State": "Registered"})
        mock_state_machine.GetIMEI = Mock(return_value={"IMEI": "123456789012345"})
        mock_state_machine.Terminate = Mock()
        
        # Patch gammu.StateMachine
        original_state_machine = gammu.StateMachine
        gammu.StateMachine = Mock(return_value=mock_state_machine)
        
        yield mock_state_machine
        
        # Restore original class
        gammu.StateMachine = original_state_machine
    except ImportError:
        # Gammu not available, create a mock module
        import sys
        gammu_mock = Mock()
        gammu_mock.StateMachine = Mock()
        gammu_mock.ERR_EMPTY = Exception("No more messages")
        sys.modules['gammu'] = gammu_mock
        yield gammu_mock


@pytest.fixture(autouse=True)
def mock_serial():
    """Mock serial library for tests."""
    import sys
    serial_mock = Mock()
    serial_mock.Serial = Mock()
    sys.modules['serial'] = serial_mock
    yield serial_mock


@pytest.fixture(autouse=True)
def mock_ollama():
    """Mock Ollama library for tests."""
    import sys
    ollama_mock = Mock()
    ollama_mock.AsyncClient = Mock()
    ollama_mock.ERR_EMPTY = Exception("No more messages")
    sys.modules['ollama'] = ollama_mock
    yield ollama_mock
