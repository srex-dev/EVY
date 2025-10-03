"""Unit tests for SMS Gateway service."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.services.sms_gateway.main import SMSGateway
from backend.services.sms_gateway.message_parser import MessageParser
from backend.services.sms_gateway.message_queue import SMSMessageQueue
from backend.shared.models import SMSMessage, MessagePriority


class TestSMSGateway:
    """Test SMS Gateway functionality."""
    
    @pytest.fixture
    def sms_gateway(self):
        """Create SMS gateway instance for testing."""
        return SMSGateway()
    
    @pytest.mark.asyncio
    async def test_gateway_initialization(self, sms_gateway, mock_message_queue):
        """Test SMS gateway initialization."""
        with patch.object(sms_gateway, 'message_queue', mock_message_queue):
            with patch.object(sms_gateway, 'gsm_driver') as mock_gsm:
                with patch.object(sms_gateway, 'serial_driver') as mock_serial:
                    mock_gsm.initialize = AsyncMock(return_value=False)
                    mock_serial.initialize = AsyncMock(return_value=False)
                    
                    result = await sms_gateway.initialize()
                    
                    # Should initialize successfully even without GSM
                    assert result is True
                    assert sms_gateway.active_driver is None
                    mock_message_queue.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_sms_success(self, sms_gateway, sample_sms_message, mock_message_queue):
        """Test successful SMS sending."""
        with patch.object(sms_gateway, 'message_queue', mock_message_queue):
            result = await sms_gateway.send_sms(sample_sms_message)
            
            assert result is True
            mock_message_queue.enqueue_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_sms_rate_limit(self, sms_gateway, sample_sms_message, mock_message_queue):
        """Test SMS rate limiting."""
        with patch.object(sms_gateway, 'message_queue', mock_message_queue):
            # Set up rate limiting
            sms_gateway.last_send_times[sample_sms_message.receiver] = datetime.utcnow()
            
            result = await sms_gateway.send_sms(sample_sms_message)
            
            assert result is False  # Should be rate limited
            mock_message_queue.enqueue_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_receive_sms_processing(self, sms_gateway, sample_sms_message):
        """Test SMS receiving and processing."""
        with patch.object(sms_gateway, 'forward_to_router', AsyncMock()) as mock_forward:
            await sms_gateway.receive_sms(sample_sms_message)
            
            # Should add message to received list
            assert len(sms_gateway.received_messages) == 1
            assert sms_gateway.received_messages[0].content == sample_sms_message.content
            
            # Should forward to router
            mock_forward.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_emergency_message_priority(self, sms_gateway, sample_emergency_message):
        """Test emergency message priority handling."""
        with patch.object(sms_gateway, 'forward_to_router', AsyncMock()):
            await sms_gateway.receive_sms(sample_emergency_message)
            
            # Emergency messages should have high priority
            received_message = sms_gateway.received_messages[0]
            assert received_message.priority == MessagePriority.EMERGENCY
    
    @pytest.mark.asyncio
    async def test_send_message_handler_success(self, sms_gateway, mock_gsm_driver):
        """Test successful message sending via handler."""
        sms_gateway.active_driver = mock_gsm_driver
        
        result = await sms_gateway._send_message_handler("+1234567890", "Test message")
        
        assert result is True
        mock_gsm_driver.send_sms.assert_called_once_with("+1234567890", "Test message")
    
    @pytest.mark.asyncio
    async def test_send_message_handler_simulation_mode(self, sms_gateway):
        """Test message sending in simulation mode."""
        sms_gateway.active_driver = None  # No GSM driver
        
        result = await sms_gateway._send_message_handler("+1234567890", "Test message")
        
        assert result is True  # Should succeed in simulation mode


class TestMessageParser:
    """Test message parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create message parser instance."""
        return MessageParser()
    
    def test_parse_emergency_message(self, parser):
        """Test parsing emergency messages."""
        message = "Help! Emergency! Fire in building!"
        parsed = parser.parse_message(message, "+1234567890")
        
        assert parsed.intent.value == "emergency"
        assert parsed.priority == "emergency"
        assert parsed.requires_rag is False  # Emergency doesn't need RAG
        assert parsed.requires_llm is True
    
    def test_parse_question_message(self, parser):
        """Test parsing question messages."""
        message = "What is the weather like today?"
        parsed = parser.parse_message(message, "+1234567890")
        
        assert parsed.intent.value == "question"
        assert parsed.category.value == "weather"
        assert parsed.requires_rag is True  # Weather questions need RAG
        assert parsed.requires_llm is True
    
    def test_parse_greeting_message(self, parser):
        """Test parsing greeting messages."""
        message = "Hello, how are you?"
        parsed = parser.parse_message(message, "+1234567890")
        
        assert parsed.intent.value == "greeting"
        assert parsed.priority == "low"
        assert parsed.requires_llm is True
    
    def test_extract_phone_numbers(self, parser):
        """Test phone number extraction."""
        message = "Call me at 555-123-4567 or +1 (555) 987-6543"
        parsed = parser.parse_message(message, "+1234567890")
        
        assert len(parsed.entities['phone_numbers']) > 0
    
    def test_extract_emails(self, parser):
        """Test email extraction."""
        message = "Contact me at test@example.com for more info"
        parsed = parser.parse_message(message, "+1234567890")
        
        assert 'test@example.com' in parsed.entities['emails']
    
    def test_validate_message_valid(self, parser):
        """Test valid message validation."""
        message = "This is a valid message under 160 characters."
        validation = parser.validate_message(message)
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
    
    def test_validate_message_too_long(self, parser):
        """Test message length validation."""
        message = "x" * 200  # Over 160 character limit
        validation = parser.validate_message(message)
        
        assert validation['valid'] is False
        assert any("too long" in error.lower() for error in validation['errors'])
    
    def test_validate_message_empty(self, parser):
        """Test empty message validation."""
        message = ""
        validation = parser.validate_message(message)
        
        assert validation['valid'] is False
        assert any("empty" in error.lower() for error in validation['errors'])
    
    def test_language_detection(self, parser):
        """Test basic language detection."""
        english_message = "Hello, how are you?"
        spanish_message = "Hola, ¿cómo estás?"
        
        english_parsed = parser.parse_message(english_message)
        spanish_parsed = parser.parse_message(spanish_message)
        
        assert english_parsed.language == "en"
        assert spanish_parsed.language == "es"


class TestMessageQueue:
    """Test message queue functionality."""
    
    @pytest.fixture
    def message_queue(self):
        """Create message queue instance."""
        return SMSMessageQueue()
    
    @pytest.mark.asyncio
    async def test_queue_initialization(self, message_queue, mock_redis):
        """Test queue initialization."""
        result = await message_queue.initialize()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_enqueue_message(self, message_queue, mock_redis):
        """Test message enqueuing."""
        message_id = await message_queue.enqueue_message(
            phone_number="+1234567890",
            content="Test message",
            priority="normal"
        )
        
        assert message_id is not None
        assert message_id.startswith("sms_")
        mock_redis.hset.assert_called()
        mock_redis.zadd.assert_called()
    
    @pytest.mark.asyncio
    async def test_dequeue_message(self, message_queue, mock_redis):
        """Test message dequeuing."""
        # Mock Redis to return a message
        mock_message_data = {
            'id': 'test_id',
            'phone_number': '+1234567890',
            'content': 'Test message',
            'priority': 'normal',
            'status': 'pending',
            'created_at': '2024-01-01T00:00:00',
            'next_retry': None,
            'attempts': '0',
            'max_attempts': '3',
            'metadata': '{}'
        }
        
        mock_redis.bzpopmin.return_value = ('queue', 'test_id', 1.0)
        mock_redis.hgetall.return_value = mock_message_data
        
        message = await message_queue.dequeue_message()
        
        assert message is not None
        assert message.phone_number == '+1234567890'
        assert message.content == 'Test message'
    
    @pytest.mark.asyncio
    async def test_mark_sent(self, message_queue, mock_redis):
        """Test marking message as sent."""
        await message_queue.mark_sent("test_message_id")
        
        mock_redis.zrem.assert_called()
        mock_redis.zadd.assert_called()
        mock_redis.hset.assert_called()
    
    @pytest.mark.asyncio
    async def test_mark_failed_retry(self, message_queue, mock_redis):
        """Test marking message as failed with retry."""
        mock_message_data = {
            'id': 'test_id',
            'attempts': '1',
            'max_attempts': '3'
        }
        mock_redis.hgetall.return_value = mock_message_data
        
        await message_queue.mark_failed("test_message_id", "Test error")
        
        # Should schedule retry since attempts < max_attempts
        mock_redis.zadd.assert_called()  # Add back to queue for retry
    
    @pytest.mark.asyncio
    async def test_mark_failed_permanent(self, message_queue, mock_redis):
        """Test marking message as permanently failed."""
        mock_message_data = {
            'id': 'test_id',
            'attempts': '3',
            'max_attempts': '3'
        }
        mock_redis.hgetall.return_value = mock_message_data
        
        await message_queue.mark_failed("test_message_id", "Test error")
        
        # Should move to failed queue since attempts >= max_attempts
        mock_redis.zadd.assert_called()  # Add to failed queue
    
    @pytest.mark.asyncio
    async def test_get_queue_stats(self, message_queue, mock_redis):
        """Test getting queue statistics."""
        mock_redis.zcard.side_effect = [5, 2, 10, 1]  # pending, processing, sent, failed
        
        stats = await message_queue.get_queue_stats()
        
        assert stats['pending'] == 5
        assert stats['processing'] == 2
        assert stats['sent'] == 10
        assert stats['failed'] == 1
        assert stats['total_messages'] == 18


@pytest.mark.asyncio
async def test_end_to_end_sms_flow():
    """Test complete SMS flow from receiving to sending response."""
    # This would be an integration test
    # For now, we'll test the components work together
    
    # Create gateway
    gateway = SMSGateway()
    
    # Mock the dependencies
    with patch.object(gateway, 'message_queue') as mock_queue:
        with patch.object(gateway, 'forward_to_router', AsyncMock()) as mock_router:
            mock_queue.initialize = AsyncMock(return_value=True)
            mock_queue.enqueue_message = AsyncMock(return_value="test_id")
            
            # Initialize gateway
            await gateway.initialize()
            
            # Create incoming message
            incoming_message = SMSMessage(
                sender="+1234567890",
                receiver="+0987654321",
                content="What's the weather like?",
                priority=MessagePriority.NORMAL
            )
            
            # Process incoming message
            await gateway.receive_sms(incoming_message)
            
            # Verify message was processed
            assert len(gateway.received_messages) == 1
            mock_router.assert_called_once()
            
            # Verify message parsing worked
            received_msg = gateway.received_messages[0]
            assert received_msg.metadata is not None
            assert 'parsed' in received_msg.metadata
