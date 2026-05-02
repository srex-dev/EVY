# EVY Hardware Validation Checklist

This checklist is for post-software validation on edge hardware. Run tests in order and log pass/fail with notes.
Use [First Hardware Bring-Up Runbook](FIRST_HARDWARE_BRINGUP_RUNBOOK.md) for the full first-node bench procedure.

## Test Order

1. GSM modem
2. LoRa radio
3. GPS
4. Power telemetry
5. Integrated node checks

Suite command and standard report:

```bash
python scripts/test_edge_hardware_suite.py \
  --gsm-device /dev/ttyUSB0 \
  --gps-device /dev/ttyAMA0 \
  --lora-frequency 915.0 \
  --power-telemetry /data/telemetry/power.json
```

Default suite artifact:

- `data/lilevy/software_reports/hardware_validation_report.json`

## 1) GSM Modem Validation

- [ ] Confirm device paths exist (`/dev/ttyUSB0` and `/dev/ttyUSB1` when GNSS is enabled)
- [ ] AT handshake works (`AT`)
- [ ] SIM status ready (`AT+CPIN?`)
- [ ] Network registration valid (`AT+CREG?`)
- [ ] Signal quality readable (`AT+CSQ`)
- [ ] Send one SMS successfully
- [ ] Receive one SMS successfully
- [ ] 60-minute send/receive reliability run without modem lockup

Command:

```bash
python scripts/test_gsm_hardware.py --device /dev/ttyUSB0 --baud 115200
```

## 2) LoRa Radio Validation

- [ ] SPI device present (`/dev/spidev0.0`)
- [ ] GPIO pin configuration succeeds (CS/DIO0/RST)
- [ ] LoRa reset cycle succeeds
- [ ] Packet transmit loop succeeds on local node
- [ ] Packet receive succeeds with second node
- [ ] Packet loss measured at short and medium range
- [ ] Frequency configured correctly for region (US: 915 MHz)

Command:

```bash
python scripts/test_lora_hardware.py --spi /dev/spidev0.0 --frequency 915.0
```

## 3) GPS Validation

- [ ] GPS serial device present (`/dev/ttyAMA0` or `/dev/ttyUSB1`)
- [ ] NMEA sentences are readable
- [ ] First fix acquired and lat/lon parse correctly
- [ ] Warm start fix time recorded
- [ ] Fix remains stable over 15 minutes

Command:

```bash
python scripts/test_gps_hardware.py --device /dev/ttyAMA0 --baud 9600 --max-seconds 180
```

## 4) Power and Battery Validation

- [ ] Telemetry source available (I2C or JSON telemetry path)
- [ ] Battery level reads consistently
- [ ] Charge/discharge transitions are detected
- [ ] Low-battery threshold behavior triggers expected software mode
- [ ] No crash or restart when battery crosses threshold

Command:

```bash
python scripts/test_power_hardware.py --telemetry-file /data/telemetry/power.json
```

## 5) Integrated Node Validation

- [ ] Cold boot succeeds and all services become healthy
- [ ] End-to-end SMS in and out succeeds
- [ ] Emergency message gets priority under normal traffic
- [ ] `!status` returns queue and battery info
- [ ] Offline mode works (no internet) for local inference path
- [ ] Reboot during queue processing does not lose critical messages

## Recommended Acceptance Gates

- GSM: no stuck modem states across a 1-hour run
- LoRa: stable TX/RX with acceptable packet loss for target range
- GPS: reliable fixes in expected environment
- Power: correct threshold behavior without service instability
- Full node: no message loss in restart and transient-failure tests

## Report Template

For each run, capture:

- Date/time and operator
- Node ID and hardware revision
- Test command
- Result (PASS/FAIL)
- Metrics (latency, packet loss, fix time, battery level)
- Notes and corrective actions
