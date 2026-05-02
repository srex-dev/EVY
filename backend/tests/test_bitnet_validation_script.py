"""Tests for the BitNet local validation script."""
import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "validate_bitnet_local_llm.py"
SPEC = importlib.util.spec_from_file_location("validate_bitnet_local_llm", SCRIPT_PATH)
validate_bitnet = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validate_bitnet)


def test_validation_report_detects_missing_files(tmp_path):
    report = validate_bitnet.build_report(
        validate_bitnet.parse_args(
            [
                "--bitnet-dir",
                str(tmp_path / "missing-runtime"),
                "--model-path",
                str(tmp_path / "missing-model.gguf"),
                "--report",
                str(tmp_path / "report.json"),
            ]
        )
    )

    assert report["pass"] is False
    assert report["checks"]["runtime_dir"]["pass"] is False
    assert report["checks"]["model"]["pass"] is False


def test_validation_report_runs_fake_inference(tmp_path):
    bitnet_dir = tmp_path / "BitNet"
    bitnet_dir.mkdir()
    run_script = bitnet_dir / "run_inference.py"
    run_script.write_text("print('EVY: fake BitNet response')\n", encoding="utf-8")
    model = tmp_path / "ggml-model-i2_s.gguf"
    model.write_text("fake model", encoding="utf-8")

    report = validate_bitnet.build_report(
        validate_bitnet.parse_args(
            [
                "--bitnet-dir",
                str(bitnet_dir),
                "--run-script",
                str(run_script),
                "--model-path",
                str(model),
                "--python",
                sys.executable,
                "--run-inference",
                "--report",
                str(tmp_path / "report.json"),
            ]
        )
    )

    assert report["pass"] is True
    assert report["inference"]["pass"] is True
    assert "fake BitNet response" in report["inference"]["stdout_tail"]
