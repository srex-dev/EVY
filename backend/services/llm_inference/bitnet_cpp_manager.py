"""BitNet.cpp local inference adapter for EVY.

This module intentionally shells out to Microsoft's bitnet.cpp runtime instead
of loading the model through transformers. The official model card notes that
the efficiency gains come from specialized kernels, not generic transformers
execution.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from backend.shared.config import settings


logger = logging.getLogger(__name__)


class BitNetCppManager:
    """Run a local BitNet b1.58 model through bitnet.cpp."""

    def __init__(self) -> None:
        self.bitnet_dir = Path(settings.bitnet_cpp_dir)
        self.model_path = Path(settings.bitnet_model_path)
        self.run_script = Path(settings.bitnet_run_script) if settings.bitnet_run_script else self.bitnet_dir / "run_inference.py"
        self.python_executable = settings.bitnet_python_executable or sys.executable
        self.model_name = settings.bitnet_model

    def is_available(self) -> bool:
        """Return whether the configured runtime and model file are present."""
        return self.run_script.exists() and self.model_path.exists()

    async def initialize(self) -> bool:
        """Check runtime availability without failing service startup."""
        available = self.is_available()
        if available:
            logger.info("BitNet runtime available: %s", self.model_path)
        else:
            logger.warning(
                "BitNet runtime unavailable. Expected script=%s model=%s",
                self.run_script,
                self.model_path,
            )
        return available

    async def generate_response(
        self,
        prompt: str,
        max_length: int = 160,
        temperature: float = 0.7,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an SMS-sized response using bitnet.cpp."""
        if not self.is_available():
            raise FileNotFoundError(
                f"BitNet runtime/model not found: script={self.run_script}, model={self.model_path}"
            )

        full_prompt = self._prepare_prompt(prompt, context)
        max_tokens = min(settings.bitnet_n_predict, max(16, max_length))
        command = [
            self.python_executable,
            str(self.run_script),
            "-m",
            str(self.model_path),
            "-p",
            full_prompt,
            "-n",
            str(max_tokens),
            "-t",
            str(settings.bitnet_threads),
            "-c",
            str(settings.bitnet_context_tokens),
            "-temp",
            str(temperature),
        ]
        if settings.bitnet_chat_mode:
            command.append("-cnv")

        started_at = time.time()
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(self.bitnet_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=settings.llm_request_timeout_seconds,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            raise TimeoutError("BitNet inference timed out")

        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")
        if process.returncode != 0:
            raise RuntimeError(f"BitNet inference failed: {stderr_text.strip() or stdout_text.strip()}")

        response = self._clean_response(stdout_text, max_length)
        return {
            "response": response,
            "model_used": self.model_name,
            "tokens_used": len(response.split()),
            "processing_time": time.time() - started_at,
            "provider": "bitnet.cpp",
            "runtime": str(self.run_script),
            "model_path": str(self.model_path),
        }

    def get_status(self) -> Dict[str, Any]:
        """Return health-check friendly runtime metadata."""
        return {
            "provider": "bitnet.cpp",
            "model": self.model_name,
            "model_path": str(self.model_path),
            "model_present": self.model_path.exists(),
            "runtime_dir": str(self.bitnet_dir),
            "run_script": str(self.run_script),
            "runtime_present": self.run_script.exists(),
            "available": self.is_available(),
            "threads": settings.bitnet_threads,
            "context_tokens": settings.bitnet_context_tokens,
            "n_predict": settings.bitnet_n_predict,
        }

    def _prepare_prompt(self, prompt: str, context: Optional[str]) -> str:
        system_prompt = (
            "You are EVY, an SMS-first local assistant. "
            "Answer in 160 characters or fewer. Be direct and practical."
        )
        parts = [system_prompt]
        if context:
            parts.append(f"Local context: {context}")
        parts.append(f"User: {prompt}")
        parts.append("EVY:")
        return "\n\n".join(parts)

    def _clean_response(self, raw_output: str, max_length: int) -> str:
        text = raw_output.strip()
        for marker in ("EVY:", "Assistant:", "assistant:", "<|assistant|>"):
            if marker in text:
                text = text.rsplit(marker, 1)[-1]

        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            lower = stripped.lower()
            if lower.startswith(("prompt eval", "eval time", "total time", "llama_", "ggml_")):
                continue
            lines.append(stripped)

        cleaned = " ".join(" ".join(lines).split())
        for artifact in ("User:", "Human:", "Assistant:", "EVY:"):
            cleaned = cleaned.replace(artifact, "")
        cleaned = cleaned.strip()
        if len(cleaned) > max_length:
            cleaned = cleaned[: max_length - 3].rstrip() + "..."
        return cleaned or "I could not generate a local response."
