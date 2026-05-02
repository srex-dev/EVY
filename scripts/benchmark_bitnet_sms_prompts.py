#!/usr/bin/env python3
"""Benchmark EVY BitNet LLM service with SMS-sized prompts.

This script is meant to run after the local BitNet runtime/model are installed
and the lilEVY LLM service is running. It sends a small fixed prompt set to the
LLM `/inference` endpoint and writes latency/response-size evidence to JSON.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "bitnet_sms_benchmark_report.json"

DEFAULT_PROMPTS = [
    "Where is the nearest shelter?",
    "How do I purify water after a storm?",
    "What should I do if my phone battery is low?",
    "EMERGENCY fire nearby, what now?",
    "How can I find a warming center?",
    "What does /status mean?",
    "Can I use tap water after flooding?",
    "Where do I get food assistance today?",
    "How do I treat a small cut?",
    "What are signs of heat exhaustion?",
    "How do I keep insulin cold in an outage?",
    "What should I pack for evacuation?",
    "How can neighbors check on elders safely?",
    "Is it safe to run a generator indoors?",
    "What should I text if I need help?",
    "How do I make an emergency contact card?",
    "What if roads are closed?",
    "How do I reduce smoke exposure?",
    "What should I do after an earthquake?",
    "How do I report a downed power line?",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark EVY BitNet SMS prompt latency")
    parser.add_argument("--base-url", default="http://127.0.0.1:18002", help="LLM service base URL")
    parser.add_argument("--prompts-file", type=Path, help="Optional JSON array or newline text prompt file")
    parser.add_argument("--max-prompts", type=int, help="Limit number of prompts for a quick run")
    parser.add_argument("--timeout", type=float, default=60.0, help="Per-request timeout in seconds")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM temperature")
    parser.add_argument("--max-length", type=int, default=160, help="Expected SMS response size")
    parser.add_argument("--p95-threshold-seconds", type=float, default=45.0, help="Pass threshold for p95 latency")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="JSON report output path")
    return parser.parse_args(argv)


def load_prompts(path: Path | None, max_prompts: int | None = None) -> list[str]:
    if path is None:
        prompts = list(DEFAULT_PROMPTS)
    else:
        text = path.read_text(encoding="utf-8")
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            loaded = [line.strip() for line in text.splitlines() if line.strip()]
        if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
            raise ValueError("Prompt file must be a JSON string array or newline-delimited text")
        prompts = [item.strip() for item in loaded if item.strip()]

    if max_prompts is not None:
        prompts = prompts[:max_prompts]
    if not prompts:
        raise ValueError("At least one prompt is required")
    return prompts


def percentile(values: Iterable[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def post_inference(base_url: str, prompt: str, timeout: float, max_length: int, temperature: float) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/inference"
    payload = {
        "prompt": prompt,
        "max_length": max_length,
        "temperature": temperature,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started_at = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(response_body)
            status_code = response.status
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "prompt": prompt,
            "pass": False,
            "status_code": None,
            "latency_seconds": round(time.time() - started_at, 3),
            "error": str(exc),
        }

    response_text = str(parsed.get("response", ""))
    return {
        "prompt": prompt,
        "pass": status_code == 200 and 0 < len(response_text) <= max_length,
        "status_code": status_code,
        "latency_seconds": round(time.time() - started_at, 3),
        "response_length": len(response_text),
        "response": response_text,
        "model_used": parsed.get("model_used"),
        "tokens_used": parsed.get("tokens_used"),
        "processing_time": parsed.get("processing_time"),
        "metadata": parsed.get("metadata"),
    }


def summarize_results(results: list[dict[str, Any]], p95_threshold_seconds: float) -> dict[str, Any]:
    latencies = [float(item["latency_seconds"]) for item in results if item.get("status_code") == 200]
    all_responses_sms_sized = all(item.get("pass", False) for item in results)
    p95 = percentile(latencies, 0.95)
    summary = {
        "total": len(results),
        "passed": sum(1 for item in results if item.get("pass")),
        "failed": sum(1 for item in results if not item.get("pass")),
        "all_responses_sms_sized": all_responses_sms_sized,
        "latency_seconds": {
            "min": round(min(latencies), 3) if latencies else 0.0,
            "max": round(max(latencies), 3) if latencies else 0.0,
            "mean": round(statistics.mean(latencies), 3) if latencies else 0.0,
            "p50": round(percentile(latencies, 0.50), 3),
            "p95": round(p95, 3),
        },
        "p95_threshold_seconds": p95_threshold_seconds,
    }
    summary["pass"] = (
        summary["failed"] == 0
        and bool(latencies)
        and p95 <= p95_threshold_seconds
        and all_responses_sms_sized
    )
    return summary


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    prompts = load_prompts(args.prompts_file, args.max_prompts)
    started_at = time.time()
    results = [
        post_inference(
            base_url=args.base_url,
            prompt=prompt,
            timeout=args.timeout,
            max_length=args.max_length,
            temperature=args.temperature,
        )
        for prompt in prompts
    ]
    summary = summarize_results(results, args.p95_threshold_seconds)
    return {
        "test": "bitnet_sms_prompt_benchmark",
        "started_at": started_at,
        "finished_at": time.time(),
        "duration_seconds": round(time.time() - started_at, 3),
        "base_url": args.base_url,
        "configuration": {
            "timeout": args.timeout,
            "temperature": args.temperature,
            "max_length": args.max_length,
            "p95_threshold_seconds": args.p95_threshold_seconds,
        },
        "summary": summary,
        "results": results,
        "pass": summary["pass"],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run_benchmark(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
