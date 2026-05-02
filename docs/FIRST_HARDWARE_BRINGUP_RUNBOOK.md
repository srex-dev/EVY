# EVY First Hardware Bring-Up Runbook

Use this when the first Raspberry Pi, GSM modem/HAT, SIM, antennas, and power hardware arrive.

Goal: prove one lilEVY node can receive one real SMS and send one real response through GSM, local BitNet, local RAG, and the router without confusing simulation with hardware.

## Bench Scope

In scope for the first bench node:

- Raspberry Pi OS
- Docker
- Python
- UART/SPI/GPIO access
- GSM modem detection
- one outbound SMS
- one inbound SMS
- integrated SMS -> router -> BitNet/RAG -> SMS response
- BitNet benchmark on real hardware
- boot self-check report
- power/thermal baseline when telemetry is available

Out of scope until after this passes:

- Meshtastic
- custom LoRa mesh routing
- NATS JetStream
- OTA updates
- Syncthing
- whisper.cpp
- bigEVY/hybrid deployment

## Required Equipment

- Raspberry Pi 5, 8 GB RAM preferred
- 64 GB or larger microSD/SSD
- reliable 5 V bench power supply
- GSM/LTE modem or HAT that supports SMS
- activated SIM with SMS service
- cellular antenna attached before modem transmit
- optional GPS antenna/source
- optional SX1276-class LoRa HAT for later SPI check
- laptop on same network
- known phone number for inbound/outbound SMS tests

## Report Artifacts

Keep every report under:

```text
data/lilevy/software_reports/
```

Standard artifacts:

- `pi_bootstrap_check_report.json`
- `boot_self_check_report.json`
- `bitnet_local_llm_report.json`
- `bitnet_sms_benchmark_report.json`
- `knowledge_pack_validation_report.json`
- `llm_rag_tuning_report.json`
- `hardware_validation_report.json`

## Phase 1: Raspberry Pi OS

1. Flash Raspberry Pi OS 64-bit.
2. Enable SSH if the Pi will be headless.
3. Boot with Ethernet or known Wi-Fi.
4. Update packages:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

5. Confirm platform:

```bash
uname -a
cat /proc/device-tree/model
python3 --version
```

## Phase 2: Enable Hardware Interfaces

Use `raspi-config` or equivalent noninteractive commands:

```bash
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial_cons 1
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo reboot
```

After reboot:

```bash
ls -l /dev/ttyAMA0 || true
ls -l /dev/ttyUSB* || true
ls -l /dev/spidev* || true
groups
```

Expected defaults:

- GSM modem: `/dev/ttyUSB0`
- GPS UART: `/dev/ttyAMA0`
- LoRa SPI: `/dev/spidev0.0`
- power telemetry: `/data/telemetry/power.json`

## Phase 3: Install Base Software

```bash
sudo apt install -y git python3 python3-venv python3-pip curl ca-certificates
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker,dialout,gpio,spi,i2c "$USER"
sudo reboot
```

After reboot:

```bash
docker version
docker compose version
groups
```

## Phase 4: Checkout EVY

```bash
git clone https://github.com/srex-dev/EVY.git
cd EVY
git checkout codex/pre-hardware-roadmap
```

Create writable paths:

```bash
mkdir -p data/lilevy/software_reports logs models
```

Set the operator phone allowlist before exposing a real SIM. Use the phone number that should be allowed to request node status:

```bash
export OPERATOR_PHONE_ALLOWLIST="+15551234567"
export PUBLIC_STATUS_ENABLED=false
```

Run the Pi bootstrap check:

```bash
python3 scripts/pi_bootstrap_check.py --require-docker
```

After GSM/GPS/SPI devices are connected, run:

```bash
python3 scripts/pi_bootstrap_check.py --require-docker --require-hardware
```

## Phase 5: Pre-Hardware Software Sanity On Pi

Before using the modem:

```bash
python3 scripts/test_software_suite.py --stage premerge
python3 scripts/validate_knowledge_pack.py --require-signature --import-sqlite --search "boil water"
python3 scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1
python3 scripts/boot_self_check.py
```

If Docker is working:

```bash
docker compose -f docker-compose.prehardware.yml config --quiet
python3 scripts/pre_hardware_compose_smoke.py --base-port 18100
```

## Phase 6: Install BitNet Runtime And Model

```bash
bash scripts/setup_bitnet_cpp.sh
```

Then start the lilEVY profile:

```bash
docker compose --env-file .env.bitnet -f docker-compose.lilevy.yml up -d --build
```

Validate:

```bash
python3 scripts/validate_bitnet_local_llm.py \
  --health-url http://127.0.0.1:18002/health \
  --run-inference

python3 scripts/benchmark_bitnet_sms_prompts.py --base-url http://127.0.0.1:18002

python3 scripts/tune_llm_rag_prompts.py \
  --llm-url http://127.0.0.1:18002 \
  --require-llm
```

Acceptance:

- BitNet health reports available.
- Benchmark records p95 latency.
- Tuning report records prompt results, even if some prompt templates need revision.

## Phase 7: GSM Modem Detection

Attach antenna before transmit. Then connect modem/HAT.

```bash
lsusb
dmesg | tail -80
ls -l /dev/ttyUSB*
```

Run:

```bash
python3 scripts/test_gsm_hardware.py --device /dev/ttyUSB0 --baud 115200
```

Expected AT evidence:

- `AT` returns `OK`
- `AT+CPIN?` returns `READY`
- `AT+CREG?` shows network registration
- `AT+CSQ` returns readable signal quality

Do not proceed to integrated SMS until this report is understandable.

## Phase 8: One Outbound SMS

Use the direct SMS hardware script only after `AT` checks pass:

```bash
python3 scripts/test_gsm_sms_hardware.py \
  --device /dev/ttyUSB0 \
  --send-to "+15551234567" \
  --message "EVY outbound GSM test"
```

Record:

- destination number
- timestamp
- exact message
- modem signal
- whether the phone received it

## Phase 9: One Inbound SMS

Send this exact first inbound test from the known phone:

```text
EVY test: what should I do if water is unsafe?
```

Then poll for it:

```bash
python3 scripts/test_gsm_sms_hardware.py \
  --device /dev/ttyUSB0 \
  --wait-inbound \
  --expect-from "+15551234567" \
  --expect-text "water is unsafe"
```

The default report is:

```text
data/lilevy/software_reports/gsm_sms_report.json
```

Record:

- sender number
- timestamp
- whether the gateway sees it
- whether response history shows it

## Phase 10: Integrated SMS Response

Start the core lilEVY profile with real GSM configuration and local BitNet/RAG.
Keep `OPERATOR_PHONE_ALLOWLIST` set for the operator phone. Leave `PUBLIC_STATUS_ENABLED=false` unless this is a closed bench simulation.

Send:

```text
How do I make water safe after flooding?
```

Acceptance:

- one real inbound SMS appears in EVY
- router classifies and processes it
- local RAG retrieves water-safety context
- BitNet or fallback produces one SMS-sized answer
- one real outbound response is received by the phone
- reports are archived
- health output clearly shows hardware vs simulation state

## Phase 11: Hardware Suite

After individual checks:

```bash
python3 scripts/test_edge_hardware_suite.py \
  --gsm-device /dev/ttyUSB0 \
  --gps-device /dev/ttyAMA0 \
  --lora-frequency 915.0 \
  --power-telemetry /data/telemetry/power.json
```

The default report is:

```text
data/lilevy/software_reports/hardware_validation_report.json
```

## Stop And Rollback

Stop services:

```bash
docker compose -f docker-compose.lilevy.yml down --remove-orphans
```

Collect logs:

```bash
docker compose -f docker-compose.lilevy.yml logs --no-color > logs/lilevy-compose.log
```

If the modem is unstable:

```bash
sudo dmesg | tail -200 > logs/pi-dmesg-tail.log
```

## Go / No-Go

Go only if:

- Pi bootstrap report passes with required software.
- GSM AT checks pass.
- one outbound SMS succeeds.
- one inbound SMS succeeds.
- integrated SMS response succeeds.
- BitNet benchmark report exists.
- boot self-check report exists.
- hardware behavior is not labeled as simulation.

No-go if:

- modem disappears under load
- SIM/network registration is unstable
- BitNet cannot run or fallback behavior is unclear
- reports are missing
- emergency or safety wording is misleading
