#!/usr/bin/env python3
"""Validate EVY's local BitNet runtime and model setup.

The default check verifies that the expected host runtime and GGUF model files
exist. Optional flags can run a short local inference or check a running EVY LLM
health endpoint.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "models" / "bitnet" / "BitNet-b1.58-2B-4T" / "ggml-model-i2_s.gguf"
DEFAULT_RUNTIME_DIR = ROOT / "third_party" / "BitNet"
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "bitnet_local_llm_report.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate BitNet local LLM setup")
    parser.add_argument("--bitnet-dir", type=Path, default=DEFAULT_RUNTIME_DIR, help="Host bitnet.cpp directory")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH, help="Host GGUF model path")
    parser.add_argument("--run-script", type=Path, help="Host run_inference.py path; defaults under --bitnet-dir")
    parser.add_argument("--python", default=sys.executable, help="Python executable for optional inference run")
    parser.add_argument("--threads", type=int, default=2, help="BitNet inference thread count")
    parser.add_argument("--context-tokens", type=int, default=512, help="BitNet context size")
    parser.add_argument("--n-predict", type=int, default=32, help="Tokens to request in optional inference run")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature for optional inference run")
    parser.add_argument(
        "--prompt",
        default="Reply in one short sentence: EVY local BitNet check.",
        help="Prompt for optional inference run",
    )
    parser.add_argument("--run-inference", action="store_true", help="Run bitnet.cpp once with the configured model")
    parser.add_argument("--health-url", help="Optional running EVY LLM /health URL to check")
    parser.add_argument("--timeout", type=float, default=60.0, help="Timeout for inference or health checks")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="JSON report path")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Write a report but exit 0 even if runtime/model are missing",
    )
    return parser.parse_args(argv)


def path_status(path: Path, expected_type: str) -> dict[str, Any]:
    exists = path.exists()
    status: dict[str, Any] = {
        "path": str(path),
        "exists": exists,
        "expected_type": expected_type,
        "pass": False,
    }
    if expected_type == "directory":
        status["is_directory"] = path.is_dir()
        status["pass"] = exists and path.is_dir()
    elif expected_type == "file":
        status["is_file"] = path.is_file()
        status["size_bytes"] = path.stat().st_size if path.is_file() else 0
        status["pass"] = exists and path.is_file() and status["size_bytes"] > 0
    return status


def check_health(url: str, timeout: float) -> dict[str, Any]:
    started_at = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            payload = json.loads(body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "url": url,
            "pass": False,
            "elapsed_seconds": round(time.time() - started_at, 3),
            "error": str(exc),
        }

    bitnet = (payload.get("details") or {}).get("bitnet") or {}
    return {
        "url": url,
        "pass": bool(bitnet.get("available")),
        "elapsed_seconds": round(time.time() - started_at, 3),
        "service_status": payload.get("status"),
        "provider": (payload.get("details") or {}).get("provider"),
        "bitnet": bitnet,
    }


def run_inference(args: argparse.Namespace, run_script: Path) -> dict[str, Any]:
    command = [
        args.python,
        str(run_script),
        "-m",
        str(args.model_path),
        "-p",
        args.prompt,
        "-n",
        str(args.n_predict),
        "-t",
        str(args.threads),
        "-c",
        str(args.context_tokens),
        "-temp",
        str(args.temperature),
        "-cnv",
    ]
    started_at = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(args.bitnet_dir),
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "pass": False,
            "command": " ".join(command),
            "elapsed_seconds": round(time.time() - started_at, 3),
            "error": f"Timed out after {exc.timeout} seconds",
        }

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    return {
        "pass": proc.returncode == 0 and bool(stdout),
        "command": " ".join(command),
        "exit_code": proc.returncode,
        "elapsed_seconds": round(time.time() - started_at, 3),
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    run_script = args.run_script or args.bitnet_dir / "run_inference.py"
    checks = {
        "runtime_dir": path_status(args.bitnet_dir, "directory"),
        "run_script": path_status(run_script, "file"),
        "model": path_status(args.model_path, "file"),
    }
    report: dict[str, Any] = {
        "test": "bitnet_local_llm_validation",
        "started_at": time.time(),
        "configuration": {
            "bitnet_dir": str(args.bitnet_dir),
            "run_script": str(run_script),
            "model_path": str(args.model_path),
            "threads": args.threads,
            "context_tokens": args.context_tokens,
            "n_predict": args.n_predict,
        },
        "checks": checks,
    }

    if args.health_url:
        report["health"] = check_health(args.health_url, args.timeout)

    if args.run_inference:
        if checks["runtime_dir"]["pass"] and checks["run_script"]["pass"] and checks["model"]["pass"]:
            report["inference"] = run_inference(args, run_script)
        else:
            report["inference"] = {
                "pass": False,
                "skipped": True,
                "reason": "BitNet runtime, run script, or model file is missing.",
            }

    required_passes = [checks["runtime_dir"]["pass"], checks["run_script"]["pass"], checks["model"]["pass"]]
    if "health" in report:
        required_passes.append(report["health"]["pass"])
    if "inference" in report:
        required_passes.append(report["inference"]["pass"])

    report["finished_at"] = time.time()
    report["duration_seconds"] = round(report["finished_at"] - report["started_at"], 3)
    report["pass"] = all(required_passes)
    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] or args.allow_missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
