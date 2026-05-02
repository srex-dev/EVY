"""Tests for the BitNet SMS benchmark helper."""
import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "benchmark_bitnet_sms_prompts.py"
SPEC = importlib.util.spec_from_file_location("benchmark_bitnet_sms_prompts", SCRIPT_PATH)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(benchmark)


def test_default_prompt_set_has_twenty_sms_prompts():
    prompts = benchmark.load_prompts(None)

    assert len(prompts) == 20
    assert all(isinstance(prompt, str) and prompt for prompt in prompts)


def test_load_prompts_from_json_and_limit(tmp_path):
    prompt_file = tmp_path / "prompts.json"
    prompt_file.write_text(json.dumps(["one", "two", "three"]), encoding="utf-8")

    prompts = benchmark.load_prompts(prompt_file, max_prompts=2)

    assert prompts == ["one", "two"]


def test_percentile_interpolates_values():
    assert benchmark.percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5
    assert round(benchmark.percentile([1.0, 2.0, 3.0, 4.0], 0.95), 2) == 3.85


def test_summarize_results_passes_sms_sized_responses():
    results = [
        {"pass": True, "status_code": 200, "latency_seconds": 1.0},
        {"pass": True, "status_code": 200, "latency_seconds": 2.0},
        {"pass": True, "status_code": 200, "latency_seconds": 3.0},
    ]

    summary = benchmark.summarize_results(results, p95_threshold_seconds=5.0)

    assert summary["pass"] is True
    assert summary["latency_seconds"]["p50"] == 2.0
    assert summary["failed"] == 0


def test_summarize_results_fails_over_threshold():
    results = [
        {"pass": True, "status_code": 200, "latency_seconds": 10.0},
        {"pass": True, "status_code": 200, "latency_seconds": 50.0},
    ]

    summary = benchmark.summarize_results(results, p95_threshold_seconds=20.0)

    assert summary["pass"] is False
