# EVY Deployment Runbook

This runbook describes the deployment paths that are currently supported or intentionally draft. It is written for pre-hardware validation first, then Raspberry Pi hardware bring-up.

## Current Deployment Status

| Path | Status | Use it for |
| --- | --- | --- |
| `docker-compose.prehardware.yml` | Verified | Containerized pre-hardware API/SMS/router/privacy flow with deterministic RAG/LLM stubs. |
| `docker-compose.yml` | Config-verified | Main service topology review; not yet the preferred first smoke path because full model/RAG dependencies are heavier. |
| `docker-compose.lilevy.yml` | Config-verified | Core Raspberry Pi/lilEVY service profile using real API/SMS/router/LLM/RAG/privacy modules. |
| `docker-compose.bigevy.yml` | Draft | Central-node design; bigEVY app entrypoint is not implemented. |
| `docker-compose.enhanced-lilevy.yml` | Experimental | LoRa/mesh design; not ready as a hardware gate. |
| `docker-compose.hybrid.yml` | Experimental | lilEVY plus bigEVY design; not ready as a hardware gate. |

## Pre-Hardware Container Smoke

Use this before hardware arrives. It builds a lightweight image, starts the real API gateway, SMS gateway, message router, and privacy filter, then uses deterministic local stubs for RAG and LLM.

```bash
python scripts/pre_hardware_compose_smoke.py
```

If ports `8000` through `8005` are busy, use another base port:

```bash
python scripts/pre_hardware_compose_smoke.py --base-port 18100
```

Expected result:

```json
{
  "pass": true,
  "report": "data/lilevy/software_reports/pre_hardware_compose_smoke_report.json"
}
```

The smoke sends:

- A normal query.
- A `/status` command.
- An emergency message.

It verifies that responses appear in SMS history and fit inside SMS-sized chunks.

## Manual Pre-Hardware Stack

Start the verified lightweight stack:

```bash
docker compose -f docker-compose.prehardware.yml up -d --wait
```

If default ports are busy:

```bash
EVY_PREHW_API_PORT=18100 \
EVY_PREHW_SMS_PORT=18101 \
EVY_PREHW_ROUTER_PORT=18102 \
EVY_PREHW_LLM_PORT=18103 \
EVY_PREHW_RAG_PORT=18104 \
EVY_PREHW_PRIVACY_PORT=18105 \
docker compose -f docker-compose.prehardware.yml up -d --wait
```

Run the external smoke against that stack:

```bash
python scripts/pre_hardware_smoke.py --external-api-url http://127.0.0.1:18100
```

Stop the stack:

```bash
docker compose -f docker-compose.prehardware.yml down --remove-orphans
```

## Main Compose Config Gate

The main Compose file should at least continue to parse cleanly:

```bash
docker compose config --quiet
```

This checks YAML shape and service URL wiring. It does not prove that every heavy dependency, model, or hardware path is ready.

## Core lilEVY Config Gate

The core lilEVY profile now uses real service entrypoints:

```bash
docker compose -f docker-compose.lilevy.yml config --quiet
```

Default host ports are intentionally high to reduce collisions on development machines:

| Service | Container port | Default host port |
| --- | --- | --- |
| API gateway | `8080` | `18080` |
| SMS gateway | `8000` | `18000` |
| Message router | `8001` | `18001` |
| Tiny LLM | `8002` | `18002` |
| Local RAG | `8003` | `18003` |
| Privacy filter | `8004` | `18004` |

Hardware device mounts are intentionally not in the base file. Add a local override after the exact modem, GPS, LoRa, and GPIO paths are confirmed.

On Linux/Raspberry Pi hardware, the current helper script wraps this profile:

```bash
./deploy-lilevy.sh
```

The script writes `.env.lilevy`, builds the core services, starts them, and checks the configured health endpoints. It also includes a local `docker-compose.override.yml` only when that file exists, so a clean checkout does not depend on an untracked override.

## Local BitNet LLM Setup

lilEVY now targets BitNet b1.58 2B4T through `bitnet.cpp` for local inference.

Prepare the runtime and model on Linux/Raspberry Pi:

```bash
bash scripts/setup_bitnet_cpp.sh
```

Then run:

```bash
docker compose --env-file .env.bitnet -f docker-compose.lilevy.yml up -d --build
```

The LLM health endpoint should report `details.bitnet.available = true`. See [BitNet Local 1-Bit LLM](BITNET_LOCAL_LLM.md) for model paths and validation notes.

Capture a local readiness report:

```bash
python scripts/validate_bitnet_local_llm.py --run-inference --health-url http://127.0.0.1:18002/health
```

Then capture the SMS prompt benchmark:

```bash
python scripts/benchmark_bitnet_sms_prompts.py
```

## First Hardware Bring-Up Order

Do not start with the full system. Bring hardware up in this order:

1. Boot Raspberry Pi and confirm OS, Python, Docker, UART, SPI, and GPIO access.
2. Confirm device paths: GSM `/dev/ttyUSB*`, GPS `/dev/ttyAMA0`, LoRa `/dev/spidev0.0`.
3. Run GSM hardware validation.
4. Send one outbound SMS.
5. Receive one inbound SMS.
6. Run LoRa SPI/GPIO validation.
7. Run GPS validation if GPS is installed.
8. Run power telemetry validation.
9. Run the integrated SMS flow with the real modem.

Hardware validation scripts:

```bash
python scripts/test_gsm_hardware.py --device /dev/ttyUSB0
python scripts/test_lora_hardware.py --spi-bus 0 --spi-device 0 --frequency 915.0
python scripts/test_gps_hardware.py --device /dev/ttyAMA0
python scripts/test_power_hardware.py --telemetry-file /data/telemetry/power.json
python scripts/test_edge_hardware_suite.py
```

## Operator Status Command

The router supports:

- `/status`
- `!status`

The response includes processed message count, RAG usage, and battery value if a telemetry file exists.

Optional power telemetry file:

```json
{"battery_level": 78.2}
```

Default path:

```text
/data/telemetry/power.json
```

## Known Deployment Gaps

- bigEVY Dockerfile still references a missing app entrypoint.
- Enhanced lilEVY/mesh deployment is not ready for first hardware validation.
- The full RAG/LLM runtime path still needs a decision: deterministic stubs, local Ollama, or a preloaded tiny model.
- Secrets, operator authentication, and public-phone policies are not production-ready.
