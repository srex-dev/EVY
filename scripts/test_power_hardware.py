#!/usr/bin/env python3
"""Basic power telemetry validation for edge nodes."""

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate power telemetry input.")
    parser.add_argument("--telemetry-file", default="/data/telemetry/power.json")
    parser.add_argument("--low-threshold", type=float, default=20.0)
    parser.add_argument("--report", default="data/lilevy/hardware_reports/power_report.json")
    args = parser.parse_args()

    report = {
        "test": "power_hardware",
        "telemetry_file": args.telemetry_file,
        "checks": {
            "telemetry_present": False,
            "battery_level_present": False,
            "battery_level_valid": False,
            "low_battery_mode_should_trigger": False,
        },
        "battery_level": None,
        "pass": False,
    }

    path = Path(args.telemetry_file)
    if path.exists():
        report["checks"]["telemetry_present"] = True
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            battery_level = payload.get("battery_level")
            if battery_level is not None:
                report["checks"]["battery_level_present"] = True
                battery_level = float(battery_level)
                report["battery_level"] = battery_level
                if 0.0 <= battery_level <= 100.0:
                    report["checks"]["battery_level_valid"] = True
                    if battery_level <= args.low_threshold:
                        report["checks"]["low_battery_mode_should_trigger"] = True
        except Exception as e:
            report["error"] = str(e)

    report["pass"] = (
        report["checks"]["telemetry_present"]
        and report["checks"]["battery_level_present"]
        and report["checks"]["battery_level_valid"]
    )

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
