"""Tests for hardware validation suite report shape."""
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "test_edge_hardware_suite.py"
SPEC = importlib.util.spec_from_file_location("test_edge_hardware_suite", SCRIPT_PATH)
hardware_suite = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(hardware_suite)


def test_hardware_suite_report_uses_standard_artifact_path():
    args = hardware_suite.parse_args([])

    assert str(args.report).endswith("data/lilevy/software_reports/hardware_validation_report.json")


def test_hardware_suite_report_marks_failed_steps_without_hardware():
    args = hardware_suite.parse_args(["--gsm-device", "/dev/missing-gsm"])

    def fake_runner(name, cmd):
        return {
            "name": name,
            "command": " ".join(cmd),
            "exit_code": 1 if name == "gsm" else 0,
            "stdout": "",
            "stderr": "missing",
            "pass": name != "gsm",
        }

    report = hardware_suite.build_report(args, runner=fake_runner)

    assert report["pass"] is False
    assert report["hardware_profile"]["gsm_device"] == "/dev/missing-gsm"
    assert report["simulation_visible"]["hardware_required"] is True
    assert report["simulation_visible"]["missing_or_failed_steps"] == ["gsm"]
