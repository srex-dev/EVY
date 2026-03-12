"""Tests for local-first routing and BitNet model registration."""
import pytest

from backend.shared.communication.smart_router import (
    SmartCommunicationRouter,
    QueryType,
    QueryComplexity,
    CommunicationLayer,
)
from backend.services.llm_inference.tiny_model_manager import TinyModelManager


@pytest.mark.asyncio
async def test_smart_router_prefers_local_layers_for_complex():
    router = SmartCommunicationRouter("node-test")
    await router._setup_routing_policies()
    policy = router.routing_policies[QueryType.LLM_REQUEST]["complexity_routing"][QueryComplexity.COMPLEX]
    assert policy[0] in (CommunicationLayer.SMS, CommunicationLayer.LORA)
    assert CommunicationLayer.INTERNET in policy


def test_bitnet_model_is_registered_for_edge():
    manager = TinyModelManager()
    models = manager.get_available_models()
    names = {m["name"] for m in models}
    assert "bitnet-2b" in names
