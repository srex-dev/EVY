#!/usr/bin/env python3
"""Write a lightweight EVY boot self-check report."""
from __future__ import annotations

import argparse
import json
import os
import platform
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "boot_self_check_report.json"


def path_check(path: str) -> dict[str, Any]:
    target = Path(path)
    return {
        "path": path,
        "exists": target.exists(),
        "is_readable": os.access(target, os.R_OK) if target.exists() else False,
        "is_writable": os.access(target, os.W_OK) if target.exists() else False,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    checks = {
        "writable_data": path_check(args.data_dir),
        "writable_logs": path_check(args.logs_dir),
        "model_cache": path_check(args.model_dir),
        "gsm_device": path_check(args.gsm_device),
        "gps_device": path_check(args.gps_device),
        "lora_spi": path_check(args.lora_spi),
        "power_telemetry": path_check(args.power_telemetry),
    }
    report = {
        "test": "boot_self_check",
        "timestamp": time.time(),
        "node_id": args.node_id,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "checks": checks,
        "simulation_visible": {
            "gsm_hardware_present": checks["gsm_device"]["exists"],
            "gps_hardware_present": checks["gps_device"]["exists"],
            "lora_hardware_present": checks["lora_spi"]["exists"],
            "power_telemetry_present": checks["power_telemetry"]["exists"],
        },
    }
    required = ["writable_data", "writable_logs", "model_cache"]
    report["pass"] = all(checks[name]["exists"] and checks[name]["is_writable"] for name in required)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write EVY boot self-check report")
    parser.add_argument("--node-id", default=os.getenv("NODE_ID", "lilevy-001"))
    parser.add_argument("--data-dir", default=os.getenv("EVY_DATA_DIR", str(ROOT / "data")))
    parser.add_argument("--logs-dir", default=os.getenv("EVY_LOGS_DIR", str(ROOT / "logs")))
    parser.add_argument("--model-dir", default=os.getenv("EVY_MODEL_DIR", str(ROOT / "models")))
    parser.add_argument("--gsm-device", default=os.getenv("GSM_DEVICE", "/dev/ttyUSB0"))
    parser.add_argument("--gps-device", default=os.getenv("GPS_DEVICE", "/dev/ttyAMA0"))
    parser.add_argument("--lora-spi", default=os.getenv("LORA_SPI_DEVICE", "/dev/spidev0.0"))
    parser.add_argument("--power-telemetry", default=os.getenv("POWER_TELEMETRY_PATH", "/data/telemetry/power.json"))
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    Path(args.logs_dir).mkdir(parents=True, exist_ok=True)
    Path(args.model_dir).mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
