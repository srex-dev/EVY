"""Tests for Raspberry Pi bootstrap readiness report."""
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "pi_bootstrap_check.py"
SPEC = importlib.util.spec_from_file_location("pi_bootstrap_check", SCRIPT_PATH)
pi_bootstrap = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(pi_bootstrap)


def _fake_command(found: bool = True):
    def checker(command: str):
        return {
            "command": command,
            "found": found,
            "path": f"/usr/bin/{command}",
            "version": "test",
        }

    return checker


def test_bootstrap_report_passes_without_required_hardware(tmp_path):
    args = pi_bootstrap.parse_args(
        [
            "--data-dir",
            str(tmp_path / "data"),
            "--logs-dir",
            str(tmp_path / "logs"),
            "--model-dir",
            str(tmp_path / "models"),
            "--gsm-device",
            str(tmp_path / "missing-gsm"),
            "--gps-device",
            str(tmp_path / "missing-gps"),
            "--lora-spi",
            str(tmp_path / "missing-spi"),
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = pi_bootstrap.build_report(args, command_checker=_fake_command(True))

    assert report["pass"] is True
    assert report["requirements"]["software_ready"] is True
    assert report["requirements"]["hardware_ready"] is None
    assert report["simulation_visible"]["gsm_hardware_present"] is False


def test_bootstrap_report_fails_when_hardware_required_and_missing(tmp_path):
    args = pi_bootstrap.parse_args(
        [
            "--data-dir",
            str(tmp_path / "data"),
            "--logs-dir",
            str(tmp_path / "logs"),
            "--model-dir",
            str(tmp_path / "models"),
            "--gsm-device",
            str(tmp_path / "missing-gsm"),
            "--gps-device",
            str(tmp_path / "missing-gps"),
            "--lora-spi",
            str(tmp_path / "missing-spi"),
            "--require-hardware",
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = pi_bootstrap.build_report(args, command_checker=_fake_command(True))

    assert report["pass"] is False
    assert report["requirements"]["software_ready"] is True
    assert report["requirements"]["hardware_ready"] is False


def test_bootstrap_report_can_require_docker(tmp_path):
    args = pi_bootstrap.parse_args(
        [
            "--data-dir",
            str(tmp_path / "data"),
            "--logs-dir",
            str(tmp_path / "logs"),
            "--model-dir",
            str(tmp_path / "models"),
            "--require-docker",
            "--report",
            str(tmp_path / "report.json"),
        ]
    )

    report = pi_bootstrap.build_report(args, command_checker=_fake_command(False))

    assert report["pass"] is False
    assert report["requirements"]["software_ready"] is False
