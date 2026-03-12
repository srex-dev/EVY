"""Tests for message router enhancements."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.services.message_router.main import MessageRouter
from backend.shared.models import SMSMessage, ProcessedMessage, MessageType, MessagePriority


@pytest.mark.asyncio
async def test_chunked_sms_response_generation():
    router = MessageRouter()
    long_text = " ".join(["chunk"] * 120)
    chunks = router._chunk_sms_response(long_text)
    assert len(chunks) > 1
    assert all(len(chunk) <= 160 for chunk in chunks)
    assert chunks[0].startswith("[1/")


@pytest.mark.asyncio
async def test_route_to_rag_filters_low_scores():
    router = MessageRouter()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "documents": ["low confidence", "high confidence"],
        "scores": [0.1, 0.9],
    }

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

    with patch("backend.services.message_router.main.httpx.AsyncClient", return_value=mock_client):
        context = await router.route_to_rag("test query")

    assert context == "high confidence"


@pytest.mark.asyncio
async def test_status_command_response_is_sms_sized():
    router = MessageRouter()
    sms = SMSMessage(sender="+1", receiver="+2", content="!status")
    processed = ProcessedMessage(
        original_message=sms,
        message_type=MessageType.COMMAND,
        priority=MessagePriority.HIGH,
        requires_llm=False,
    )
    response = await router._handle_command(sms, processed)
    assert len(response) <= 160
    assert "Status OK" in response
