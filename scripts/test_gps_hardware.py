#!/usr/bin/env python3
"""Basic GPS hardware validation (NMEA stream and first fix)."""

import argparse
import json
import time
from pathlib import Path

try:
    import serial
except ImportError:
    serial = None

try:
    import pynmea2
except ImportError:
    pynmea2 = None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GPS serial stream.")
    parser.add_argument("--device", default="/dev/ttyAMA0")
    parser.add_argument("--baud", type=int, default=9600)
    parser.add_argument("--max-seconds", type=int, default=180)
    parser.add_argument("--report", default="data/lilevy/hardware_reports/gps_report.json")
    args = parser.parse_args()

    report = {
        "test": "gps_hardware",
        "device": args.device,
        "baud": args.baud,
        "checks": {
            "nmea_seen": False,
            "fix_found": False,
        },
        "fix": None,
        "pass": False,
    }

    if serial is None:
        print("pyserial not installed. Install with: pip install pyserial")
        return 2

    start = time.time()
    try:
        with serial.Serial(args.device, args.baud, timeout=1) as ser:
            while time.time() - start < args.max_seconds:
                line = ser.readline().decode("ascii", errors="replace").strip()
                if not line.startswith("$"):
                    continue
                report["checks"]["nmea_seen"] = True
                if pynmea2 is None:
                    continue
                try:
                    msg = pynmea2.parse(line)
                    lat = getattr(msg, "latitude", None)
                    lon = getattr(msg, "longitude", None)
                    if lat and lon:
                        report["checks"]["fix_found"] = True
                        report["fix"] = {"lat": float(lat), "lon": float(lon)}
                        break
                except Exception:
                    continue
    except Exception as e:
        report["error"] = str(e)

    report["elapsed_seconds"] = round(time.time() - start, 2)
    report["pass"] = report["checks"]["nmea_seen"] and report["checks"]["fix_found"]

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
