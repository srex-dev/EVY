#!/usr/bin/env python3
"""Basic GSM hardware validation for edge nodes."""

import argparse
import json
import time
from pathlib import Path

try:
    import serial
except ImportError:
    serial = None


def send_at(ser, command: str, timeout_s: float = 3.0) -> str:
    ser.reset_input_buffer()
    ser.write(f"{command}\r\n".encode())
    deadline = time.time() + timeout_s
    chunks = []
    while time.time() < deadline:
        if ser.in_waiting:
            chunks.append(ser.read(ser.in_waiting).decode("utf-8", errors="ignore"))
            text = "".join(chunks)
            if "OK" in text or "ERROR" in text:
                break
        time.sleep(0.05)
    return "".join(chunks).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GSM modem health.")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--report", default="data/lilevy/hardware_reports/gsm_report.json")
    args = parser.parse_args()

    report = {
        "test": "gsm_hardware",
        "device": args.device,
        "baud": args.baud,
        "checks": {},
        "pass": False,
    }

    if serial is None:
        print("pyserial not installed. Install with: pip install pyserial")
        return 2

    try:
        with serial.Serial(args.device, args.baud, timeout=1, write_timeout=1) as ser:
            report["checks"]["at"] = send_at(ser, "AT")
            report["checks"]["sim"] = send_at(ser, "AT+CPIN?")
            report["checks"]["network"] = send_at(ser, "AT+CREG?")
            report["checks"]["signal"] = send_at(ser, "AT+CSQ")
            report["pass"] = (
                "OK" in report["checks"]["at"]
                and ("READY" in report["checks"]["sim"] or "OK" in report["checks"]["sim"])
            )
    except Exception as e:
        report["error"] = str(e)

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
