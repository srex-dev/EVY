#!/usr/bin/env python3
"""Run all edge hardware validation scripts and summarize results."""

import argparse
import json
import subprocess
import sys
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full edge hardware validation suite.")
    parser.add_argument("--report", default="data/lilevy/hardware_reports/hardware_suite_report.json")
    parser.add_argument("--gsm-device", default="/dev/ttyUSB0")
    parser.add_argument("--gps-device", default="/dev/ttyAMA0")
    parser.add_argument("--lora-frequency", default="915.0")
    parser.add_argument("--power-telemetry", default="/data/telemetry/power.json")
    args = parser.parse_args()

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

    results = [run_step(name, cmd) for name, cmd in steps]
    suite_pass = all(item["pass"] for item in results)

    report = {
        "test": "edge_hardware_suite",
        "pass": suite_pass,
        "results": results,
    }

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if suite_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
