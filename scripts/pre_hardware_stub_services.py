"""Deterministic local stubs for pre-hardware smoke tests.

The smoke runner starts this app on separate ports for LLM and RAG so the
real message-router code can exercise HTTP service calls without needing a
downloaded model, internet access, or a populated vector database.
"""
import os
import time
from typing import Any, Dict

from fastapi import FastAPI


SERVICE_NAME = os.getenv("STUB_SERVICE_NAME", "pre-hardware-stub")

app = FastAPI(
    title="EVY Pre-Hardware Stub Services",
    description="Local deterministic LLM/RAG endpoints for simulated EVY flow checks",
    version="1.0.0",
)


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Return a service-health-shaped payload."""
    return {
        "service_name": SERVICE_NAME,
        "status": "healthy",
        "version": "1.0.0",
        "details": {"mode": "deterministic-stub"},
    }


@app.post("/inference")
async def inference(request: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deterministic SMS-sized response."""
    prompt = str(request.get("prompt", "")).strip()
    context = str(request.get("context") or "").strip()
    response = "EVY simulated answer: shelter info is available locally. Reply /status for node status."
    if "weather" in prompt.lower():
        response = "EVY simulated answer: weather data is offline in this smoke test."
    elif context:
        response = "EVY simulated answer: local context found and response path is working."

    return {
        "response": response[:160],
        "model_used": "pre-hardware-stub",
        "tokens_used": min(32, max(1, len(response.split()))),
        "processing_time": 0.01,
        "metadata": {
            "prompt_length": len(prompt),
            "has_context": bool(context),
            "generated_at": time.time(),
        },
    }


@app.post("/search")
async def search(request: Dict[str, Any]) -> Dict[str, Any]:
    """Return deterministic local context for RAG-required requests."""
    query = str(request.get("query", "")).strip()
    document = (
        "Local context: the simulated shelter desk is open, and the EVY "
        "message path can retrieve local knowledge before responding."
    )
    return {
        "documents": [document],
        "scores": [0.98],
        "metadata": [{"source": "pre_hardware_stub", "query": query}],
    }
