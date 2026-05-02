#!/usr/bin/env python3
"""Write a Raspberry Pi bootstrap readiness report for EVY lilEVY."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "data" / "lilevy" / "software_reports" / "pi_bootstrap_check_report.json"


def path_status(path: str | Path, *, create: bool = False) -> dict[str, Any]:
    target = Path(path)
    if create:
        target.mkdir(parents=True, exist_ok=True)
    exists = target.exists()
    return {
        "path": str(target),
        "exists": exists,
        "is_dir": target.is_dir() if exists else False,
        "is_file": target.is_file() if exists else False,
        "is_readable": os.access(target, os.R_OK) if exists else False,
        "is_writable": os.access(target, os.W_OK) if exists else False,
    }


def command_status(command: str) -> dict[str, Any]:
    executable = shutil.which(command)
    status = {
        "command": command,
        "found": executable is not None,
        "path": executable,
        "version": None,
    }
    if executable:
        version_cmd = [command, "--version"]
        if command == "docker":
            version_cmd = [command, "version", "--format", "{{.Client.Version}}"]
        try:
            proc = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                status["version"] = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
            else:
                status["version_error"] = proc.stderr.strip()
        except Exception as exc:
            status["version_error"] = str(exc)
    return status


def user_groups() -> list[str]:
    if platform.system().lower() != "linux":
        return []
    try:
        proc = subprocess.run(["id", "-nG"], capture_output=True, text=True, timeout=5)
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return sorted(group for group in proc.stdout.strip().split() if group)


def raspberry_pi_model() -> Optional[str]:
    model_path = Path("/proc/device-tree/model")
    if not model_path.exists():
        return None
    try:
        return model_path.read_text(encoding="utf-8", errors="ignore").replace("\x00", "").strip()
    except Exception:
        return None


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Raspberry Pi lilEVY bootstrap readiness.")
    parser.add_argument("--node-id", default=os.getenv("NODE_ID", "lilevy-001"))
    parser.add_argument("--data-dir", default=os.getenv("EVY_DATA_DIR", str(ROOT / "data")))
    parser.add_argument("--logs-dir", default=os.getenv("EVY_LOGS_DIR", str(ROOT / "logs")))
    parser.add_argument("--model-dir", default=os.getenv("EVY_MODEL_DIR", str(ROOT / "models")))
    parser.add_argument("--gsm-device", default=os.getenv("GSM_DEVICE", "/dev/ttyUSB0"))
    parser.add_argument("--gps-device", default=os.getenv("GPS_DEVICE", "/dev/ttyAMA0"))
    parser.add_argument("--lora-spi", default=os.getenv("LORA_SPI_DEVICE", "/dev/spidev0.0"))
    parser.add_argument("--bitnet-dir", default=os.getenv("BITNET_CPP_DIR", str(ROOT / "third_party" / "BitNet")))
    parser.add_argument(
        "--bitnet-model-path",
        default=os.getenv(
            "BITNET_MODEL_PATH",
            str(ROOT / "models" / "bitnet" / "BitNet-b1.58-2B-4T" / "ggml-model-i2_s.gguf"),
        ),
    )
    parser.add_argument("--require-docker", action="store_true", help="Fail if Docker CLI is missing")
    parser.add_argument("--require-hardware", action="store_true", help="Fail if GSM/GPS/SPI devices are missing")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def build_report(
    args: argparse.Namespace,
    *,
    command_checker: Callable[[str], dict[str, Any]] = command_status,
) -> dict[str, Any]:
    groups = user_groups()
    required_group_names = ["dialout", "docker", "gpio", "spi", "i2c"]
    group_checks = {group: group in groups for group in required_group_names}
    commands = {
        "python": command_checker(sys.executable),
        "docker": command_checker("docker"),
        "git": command_checker("git"),
    }
    paths = {
        "data_dir": path_status(args.data_dir, create=True),
        "logs_dir": path_status(args.logs_dir, create=True),
        "model_dir": path_status(args.model_dir, create=True),
        "compose_lilevy": path_status(ROOT / "docker-compose.lilevy.yml"),
        "compose_prehardware": path_status(ROOT / "docker-compose.prehardware.yml"),
        "bitnet_dir": path_status(args.bitnet_dir),
        "bitnet_model": path_status(args.bitnet_model_path),
    }
    devices = {
        "gsm_device": path_status(args.gsm_device),
        "gps_device": path_status(args.gps_device),
        "lora_spi": path_status(args.lora_spi),
    }
    platform_info = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "raspberry_pi_model": raspberry_pi_model(),
    }

    software_required = [
        commands["git"]["found"],
        paths["data_dir"]["is_writable"],
        paths["logs_dir"]["is_writable"],
        paths["model_dir"]["is_writable"],
        paths["compose_lilevy"]["is_file"],
        paths["compose_prehardware"]["is_file"],
    ]
    if args.require_docker:
        software_required.append(commands["docker"]["found"])

    hardware_required = []
    if args.require_hardware:
        hardware_required.extend(device["exists"] for device in devices.values())

    report = {
        "test": "pi_bootstrap_check",
        "timestamp": time.time(),
        "node_id": args.node_id,
        "platform": platform_info,
        "commands": commands,
        "groups": {
            "current": groups,
            "required_for_pi": group_checks,
        },
        "paths": paths,
        "devices": devices,
        "requirements": {
            "require_docker": args.require_docker,
            "require_hardware": args.require_hardware,
            "software_ready": all(software_required),
            "hardware_ready": all(hardware_required) if hardware_required else None,
        },
        "simulation_visible": {
            "running_on_raspberry_pi": bool(platform_info["raspberry_pi_model"]),
            "gsm_hardware_present": devices["gsm_device"]["exists"],
            "gps_hardware_present": devices["gps_device"]["exists"],
            "lora_hardware_present": devices["lora_spi"]["exists"],
            "bitnet_runtime_present": paths["bitnet_dir"]["exists"],
            "bitnet_model_present": paths["bitnet_model"]["is_file"],
        },
    }
    report["pass"] = report["requirements"]["software_ready"] and (
        report["requirements"]["hardware_ready"] is not False
    )
    return report


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "report": str(args.report)}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
