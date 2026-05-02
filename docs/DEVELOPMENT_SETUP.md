# EVY Development Setup

This guide sets up the current repository for pre-hardware development and validation.

## Required Tools

- Python 3.11.
- Node.js 20 or another current LTS compatible with Vite 5.
- Rust stable toolchain with Cargo.
- Docker Desktop or Docker Engine with Compose v2.

## Python Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

On Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Run backend tests:

```bash
python -m pytest backend/tests -q
python scripts/test_software_suite.py --stage full
```

## Frontend Setup

```bash
cd frontend
npm install
npm run build
```

Use `VITE_API_URL` for Vite environments. `REACT_APP_API_URL` is retained only as a legacy fallback.

## Rust Setup

Rust crates live under `backend/rust_services/`.

```bash
cd backend/rust_services/sms_gateway
cargo test

cd ../message_router
cargo test

cd ../compression
cargo test
```

The Rust crates now pass as standalone crates. They are not yet active Python runtime dependencies.

## Pre-Hardware Smoke Tests

Fast local-process smoke:

```bash
python scripts/pre_hardware_smoke.py
```

Containerized smoke:

```bash
python scripts/pre_hardware_compose_smoke.py
```

Use another base port if local ports are busy:

```bash
python scripts/pre_hardware_compose_smoke.py --base-port 18100
```

## Compose Checks

Main Compose config parse:

```bash
docker compose config --quiet
```

Verified lightweight pre-hardware profile:

```bash
docker compose -f docker-compose.prehardware.yml config --quiet
docker compose -f docker-compose.prehardware.yml build
```

Config-verified core lilEVY profile:

```bash
docker compose -f docker-compose.lilevy.yml config --quiet
```

The Linux/Raspberry Pi helper for that profile is:

```bash
./deploy-lilevy.sh
```

## Local BitNet LLM

EVY targets BitNet b1.58 2B4T through `bitnet.cpp` as the local lilEVY model.

On Linux/Raspberry Pi:

```bash
bash scripts/setup_bitnet_cpp.sh
```

Then check:

```bash
curl http://127.0.0.1:18002/health
```

The BitNet status should show `available: true` before hardware field testing.

Validate host files and optional local inference:

```bash
python scripts/validate_bitnet_local_llm.py
python scripts/validate_bitnet_local_llm.py --run-inference
```

Benchmark SMS-sized prompt latency once the LLM service is running:

```bash
python scripts/benchmark_bitnet_sms_prompts.py
```

## Current Validation Matrix

Before handing work to hardware bring-up:

```bash
python -m pytest backend/tests -q
python scripts/test_software_suite.py --stage full
python scripts/pre_hardware_compose_smoke.py --base-port 18100
cd frontend && npm run build
cd ../backend/rust_services/sms_gateway && cargo test
cd ../message_router && cargo test
cd ../compression && cargo test
cd ../../../.. && docker compose config --quiet
```

## Notes

- `target/`, `node_modules/`, generated data, local DB files, and Docker build context noise are ignored.
- `npm audit` currently reports a Vite/esbuild dev-server advisory. The fix path is a breaking Vite upgrade and should be handled as an explicit dependency task.
- Hardware scripts should wait until actual GSM, LoRa, GPS, and power telemetry devices are connected.
- BitNet performance still needs to be measured on the target Pi after `scripts/setup_bitnet_cpp.sh` completes.
