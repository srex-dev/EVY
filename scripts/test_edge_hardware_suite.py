#!/usr/bin/env python3
"""Run all edge hardware validation scripts and summarize results."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def run_step(name: str, cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "name": name,
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "pass": proc.returncode == 0,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full edge hardware validation suite.")
    parser.add_argument("--report", default="data/lilevy/software_reports/hardware_validation_report.json")
    parser.add_argument("--gsm-device", default="/dev/ttyUSB0")
    parser.add_argument("--gps-device", default="/dev/ttyAMA0")
    parser.add_argument("--lora-frequency", default="915.0")
    parser.add_argument("--power-telemetry", default="/data/telemetry/power.json")
    return parser.parse_args(argv)


def build_report(args: argparse.Namespace, runner=run_step) -> dict:
    steps = [
        (
            "gsm",
            [sys.executable, "scripts/test_gsm_hardware.py", "--device", args.gsm_device],
        ),
        (
            "lora",
            [sys.executable, "scripts/test_lora_hardware.py", "--frequency", args.lora_frequency],
        ),
        (
            "gps",
            [sys.executable, "scripts/test_gps_hardware.py", "--device", args.gps_device],
        ),
        (
            "power",
            [sys.executable, "scripts/test_power_hardware.py", "--telemetry-file", args.power_telemetry],
        ),
    ]

    results = [runner(name, cmd) for name, cmd in steps]
    suite_pass = all(item["pass"] for item in results)

    return {
        "test": "edge_hardware_suite",
        "timestamp": time.time(),
        "hardware_profile": {
            "gsm_device": args.gsm_device,
            "gps_device": args.gps_device,
            "lora_frequency": args.lora_frequency,
            "power_telemetry": args.power_telemetry,
        },
        "simulation_visible": {
            "hardware_suite_executed": True,
            "hardware_required": True,
            "missing_or_failed_steps": [item["name"] for item in results if not item["pass"]],
        },
        "pass": suite_pass,
        "results": results,
    }


def main() -> int:
    args = parse_args()
    report = build_report(args)

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if suite_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
