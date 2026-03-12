#!/usr/bin/env python3
"""Basic LoRa hardware validation for SX1276-class radios."""

import argparse
import json
import os
import time
from pathlib import Path

try:
    import spidev
except ImportError:
    spidev = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate LoRa SPI/GPIO wiring.")
    parser.add_argument("--spi", default="/dev/spidev0.0")
    parser.add_argument("--cs-pin", type=int, default=25)
    parser.add_argument("--dio0-pin", type=int, default=4)
    parser.add_argument("--reset-pin", type=int, default=17)
    parser.add_argument("--frequency", type=float, default=915.0)
    parser.add_argument("--report", default="data/lilevy/hardware_reports/lora_report.json")
    args = parser.parse_args()

    report = {
        "test": "lora_hardware",
        "spi_device": args.spi,
        "frequency_mhz": args.frequency,
        "checks": {
            "spi_device_exists": os.path.exists(args.spi),
            "spidev_installed": spidev is not None,
            "gpio_installed": GPIO is not None,
            "gpio_configured": False,
            "spi_transfer_ok": False,
            "radio_reset_ok": False,
        },
        "pass": False,
    }

    spi_handle = None
    try:
        if spidev is not None:
            spi_handle = spidev.SpiDev()
            spi_handle.open(0, 0)
            spi_handle.max_speed_hz = 5000000
            spi_handle.xfer2([0x42, 0x00])
            report["checks"]["spi_transfer_ok"] = True

        if GPIO is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(args.cs_pin, GPIO.OUT)
            GPIO.setup(args.dio0_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(args.reset_pin, GPIO.OUT)
            report["checks"]["gpio_configured"] = True
            GPIO.output(args.reset_pin, GPIO.LOW)
            time.sleep(0.01)
            GPIO.output(args.reset_pin, GPIO.HIGH)
            report["checks"]["radio_reset_ok"] = True

        report["pass"] = (
            report["checks"]["spi_device_exists"]
            and report["checks"]["spidev_installed"]
            and report["checks"]["gpio_installed"]
            and report["checks"]["spi_transfer_ok"]
            and report["checks"]["radio_reset_ok"]
        )
    except Exception as e:
        report["error"] = str(e)
    finally:
        if spi_handle is not None:
            spi_handle.close()
        if GPIO is not None:
            GPIO.cleanup()

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
