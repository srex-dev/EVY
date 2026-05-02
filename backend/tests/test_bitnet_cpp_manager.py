"""Tests for the BitNet.cpp local inference adapter."""
import sys

import pytest

from backend.services.llm_inference.bitnet_cpp_manager import BitNetCppManager
from backend.shared.config import settings


def test_bitnet_manager_reports_missing_runtime(tmp_path, monkeypatch):
    """Unavailable runtime/model should be explicit in health metadata."""
    monkeypatch.setattr(settings, "bitnet_cpp_dir", str(tmp_path / "missing-runtime"))
    monkeypatch.setattr(settings, "bitnet_model_path", str(tmp_path / "missing-model.gguf"))
    monkeypatch.setattr(settings, "bitnet_run_script", None)

    manager = BitNetCppManager()
    status = manager.get_status()

    assert status["available"] is False
    assert status["runtime_present"] is False
    assert status["model_present"] is False


@pytest.mark.asyncio
async def test_bitnet_manager_runs_configured_script(tmp_path, monkeypatch):
    """The adapter should call a local bitnet.cpp-compatible script."""
    bitnet_dir = tmp_path / "BitNet"
    bitnet_dir.mkdir()
    script = bitnet_dir / "run_inference.py"
    script.write_text(
        "import sys\n"
        "print('EVY: Local BitNet answer from test runtime.')\n",
        encoding="utf-8",
    )
    model = tmp_path / "ggml-model-i2_s.gguf"
    model.write_text("fake-model", encoding="utf-8")

    monkeypatch.setattr(settings, "bitnet_cpp_dir", str(bitnet_dir))
    monkeypatch.setattr(settings, "bitnet_model_path", str(model))
    monkeypatch.setattr(settings, "bitnet_run_script", str(script))
    monkeypatch.setattr(settings, "bitnet_python_executable", sys.executable)
    monkeypatch.setattr(settings, "llm_request_timeout_seconds", 5.0)

    manager = BitNetCppManager()
    result = await manager.generate_response("hello", max_length=160)

    assert result["provider"] == "bitnet.cpp"
    assert result["model_used"] == settings.bitnet_model
    assert result["response"] == "Local BitNet answer from test runtime."
