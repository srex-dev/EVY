#!/usr/bin/env python3
"""Send and/or receive one real SMS through a GSM modem using AT commands."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Optional

try:
    import serial
except ImportError:
    serial = None


DEFAULT_REPORT = "data/lilevy/software_reports/gsm_sms_report.json"
CTRL_Z = b"\x1a"


def normalize_phone_number(phone_number: str) -> str:
    stripped = phone_number.strip()
    if stripped.startswith("+"):
        prefix = "+"
    else:
        prefix = "+"
    digits = "".join(char for char in stripped if char.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    return f"{prefix}{digits}" if digits else stripped


def wait_for_response(ser, timeout_s: float, *, terminal_tokens: tuple[str, ...] = ("OK", "ERROR")) -> str:
    deadline = time.time() + timeout_s
    chunks: list[str] = []
    while time.time() < deadline:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            chunks.append(chunk)
            text = "".join(chunks)
            if any(token in text for token in terminal_tokens):
                break
        time.sleep(0.05)
    return "".join(chunks).strip()


def send_at(ser, command: str, timeout_s: float = 5.0) -> str:
    ser.reset_input_buffer()
    ser.write(f"{command}\r\n".encode("utf-8"))
    return wait_for_response(ser, timeout_s)


def send_sms(ser, phone_number: str, message: str, timeout_s: float = 30.0) -> dict[str, Any]:
    normalized = normalize_phone_number(phone_number)
    result = {
        "to": normalized,
        "message": message,
        "steps": {},
        "pass": False,
    }
    result["steps"]["text_mode"] = send_at(ser, "AT+CMGF=1")
    if "OK" not in result["steps"]["text_mode"]:
        return result

    ser.reset_input_buffer()
    ser.write(f'AT+CMGS="{normalized}"\r\n'.encode("utf-8"))
    prompt = wait_for_response(ser, 5.0, terminal_tokens=(">", "ERROR"))
    result["steps"]["cmgs_prompt"] = prompt
    if ">" not in prompt:
        return result

    ser.write(message.encode("utf-8") + CTRL_Z)
    send_response = wait_for_response(ser, timeout_s)
    result["steps"]["send_response"] = send_response
    result["pass"] = "+CMGS" in send_response and "OK" in send_response
    return result


def parse_cmgl_messages(raw: str) -> list[dict[str, Any]]:
    """Parse simple AT+CMGL text-mode output."""
    messages: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None
    for line in [item.strip() for item in raw.splitlines() if item.strip()]:
        if line.startswith("+CMGL:"):
            if current:
                messages.append(current)
            header = line[len("+CMGL:") :].strip()
            parts = [part.strip().strip('"') for part in header.split(",")]
            current = {
                "index": int(parts[0]) if parts and parts[0].isdigit() else None,
                "status": parts[1] if len(parts) > 1 else "",
                "sender": parts[2] if len(parts) > 2 else "",
                "timestamp": parts[4] if len(parts) > 4 else "",
                "content": "",
            }
        elif current and line not in {"OK", "ERROR"}:
            current["content"] = f"{current['content']}\n{line}".strip()
    if current:
        messages.append(current)
    return messages


def receive_sms(
    ser,
    *,
    expected_from: Optional[str],
    expected_text: Optional[str],
    timeout_s: float,
    poll_interval_s: float,
) -> dict[str, Any]:
    expected_sender = normalize_phone_number(expected_from) if expected_from else None
    deadline = time.time() + timeout_s
    attempts = 0
    last_raw = ""
    while time.time() < deadline:
        attempts += 1
        send_at(ser, "AT+CMGF=1")
        raw = send_at(ser, 'AT+CMGL="ALL"', timeout_s=10.0)
        last_raw = raw
        messages = parse_cmgl_messages(raw)
        for message in messages:
            sender_ok = not expected_sender or normalize_phone_number(message.get("sender", "")) == expected_sender
            text_ok = not expected_text or expected_text.lower() in message.get("content", "").lower()
            if sender_ok and text_ok:
                return {
                    "pass": True,
                    "attempts": attempts,
                    "matched_message": message,
                    "messages_seen": messages,
                    "raw_tail": raw[-2000:],
                }
        time.sleep(poll_interval_s)

    return {
        "pass": False,
        "attempts": attempts,
        "matched_message": None,
        "messages_seen": parse_cmgl_messages(last_raw),
        "raw_tail": last_raw[-2000:],
    }


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate real GSM SMS send/receive.")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--send-to", help="Phone number for one outbound SMS")
    parser.add_argument("--message", default="EVY GSM hardware test")
    parser.add_argument("--wait-inbound", action="store_true", help="Poll modem for one inbound SMS")
    parser.add_argument("--expect-from", help="Expected inbound sender")
    parser.add_argument("--expect-text", help="Expected text fragment in inbound SMS")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    report: dict[str, Any] = {
        "test": "gsm_sms_hardware",
        "device": args.device,
        "baud": args.baud,
        "send_requested": bool(args.send_to),
        "receive_requested": args.wait_inbound,
        "checks": {},
        "pass": False,
    }
    if serial is None:
        report["error"] = "pyserial not installed. Install with: pip install pyserial"
        return report

    try:
        with serial.Serial(args.device, args.baud, timeout=1, write_timeout=5) as ser:
            report["checks"]["at"] = send_at(ser, "AT")
            report["checks"]["sim"] = send_at(ser, "AT+CPIN?")
            report["checks"]["signal"] = send_at(ser, "AT+CSQ")
            if args.send_to:
                report["outbound"] = send_sms(ser, args.send_to, args.message, timeout_s=args.timeout)
            if args.wait_inbound:
                report["inbound"] = receive_sms(
                    ser,
                    expected_from=args.expect_from,
                    expected_text=args.expect_text,
                    timeout_s=args.timeout,
                    poll_interval_s=args.poll_interval,
                )
    except Exception as exc:
        report["error"] = str(exc)

    requested_results = []
    if args.send_to:
        requested_results.append(bool(report.get("outbound", {}).get("pass")))
    if args.wait_inbound:
        requested_results.append(bool(report.get("inbound", {}).get("pass")))
    base_ok = "OK" in report["checks"].get("at", "") and (
        "READY" in report["checks"].get("sim", "") or "OK" in report["checks"].get("sim", "")
    )
    report["pass"] = base_ok and bool(requested_results) and all(requested_results)
    return report


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
