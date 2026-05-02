"""Tests for pre-hardware observability names and boot self-check."""
import argparse
import importlib.util
from pathlib import Path

from backend.shared.observability import ALL_METRIC_NAMES, MetricNames


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "boot_self_check.py"
SPEC = importlib.util.spec_from_file_location("boot_self_check", SCRIPT_PATH)
boot_self_check = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(boot_self_check)


def test_metric_names_are_stable_and_unique():
    assert len(ALL_METRIC_NAMES) == len(set(ALL_METRIC_NAMES))
    assert MetricNames.SMS_RECEIVE_TO_RESPONSE_LATENCY_MS in ALL_METRIC_NAMES
    assert MetricNames.BITNET_INFERENCE_LATENCY_MS in ALL_METRIC_NAMES
    assert MetricNames.RAG_SEARCH_LATENCY_MS in ALL_METRIC_NAMES
    assert MetricNames.EMERGENCY_MESSAGE_COUNT in ALL_METRIC_NAMES
    assert MetricNames.POWER_BATTERY_VOLTAGE in ALL_METRIC_NAMES


def test_boot_self_check_report_distinguishes_missing_hardware(tmp_path):
    data_dir = tmp_path / "data"
    logs_dir = tmp_path / "logs"
    model_dir = tmp_path / "models"
    data_dir.mkdir()
    logs_dir.mkdir()
    model_dir.mkdir()
    args = argparse.Namespace(
        node_id="test-node",
        data_dir=str(data_dir),
        logs_dir=str(logs_dir),
        model_dir=str(model_dir),
        gsm_device=str(tmp_path / "missing-gsm"),
        gps_device=str(tmp_path / "missing-gps"),
        lora_spi=str(tmp_path / "missing-spi"),
        power_telemetry=str(tmp_path / "missing-power.json"),
    )

    report = boot_self_check.build_report(args)

    assert report["pass"] is True
    assert report["simulation_visible"]["gsm_hardware_present"] is False
    assert report["simulation_visible"]["power_telemetry_present"] is False
    assert report["checks"]["writable_data"]["is_writable"] is True
