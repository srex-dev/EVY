# EVY

EVY is an SMS-first AI assistant and edge-node prototype for communities that may have unreliable internet, limited power, or disaster-response communication needs. The project is organized around a small field node, `lilEVY`, and an optional central server, `bigEVY`.

This README reflects the current codebase state after a fresh review. It separates what is implemented today from what is designed, simulated, experimental, or still blocked before hardware testing.

## Current Status

| Area | Current state |
| --- | --- |
| Python backend services | Implemented prototype services for SMS gateway, message routing, LLM inference, RAG, privacy filtering, emergency detection, edge database, and service integration helpers. The curated software validation suite and full backend pytest suite pass. |
| Full Python test suite | Green in this workspace: `python -m pytest backend/tests -q` passes with the current backend tests. |
| Rust critical-path services | SMS gateway, message router, and compression crates now pass `cargo test`. The Python integration layer still uses fallbacks rather than compiled PyO3 modules. |
| Frontend dashboard | React/Vite dashboard exists for service health, message history, knowledge stats, and static settings views. `npm install` and `npm run build` pass; several UI controls are still display-only. |
| Local LLM | Target local model is BitNet b1.58 2B4T through `bitnet.cpp`. The repo has a native adapter, setup script, Compose env, and health reporting; target Raspberry Pi latency/power is still unmeasured. |
| Local RAG and knowledge packs | Current default RAG remains ChromaDB plus the local document manager. A feature-flagged SQLite FTS5 RAG store, v1 knowledge-pack manifest validator/importer, and Plus Code SMS metadata parser are implemented for pre-hardware trials. |
| Hardware integration | GSM, LoRa, GPS, and power telemetry code paths and validation scripts exist. They have not been validated on target Raspberry Pi hardware in this repo. |
| Simulated SMS flow | Deterministic pre-hardware smoke test passes for normal query, command, and emergency messages using real API/SMS/router/privacy services plus local LLM/RAG stubs. |
| Deployment | `docker-compose.prehardware.yml` builds, starts, passes the container smoke test, and shuts down cleanly. `docker-compose.lilevy.yml` now points at real Python service modules and parses cleanly. The main, bigEVY, enhanced lilEVY, and hybrid Compose files also parse; bigEVY/enhanced/hybrid remain draft/experimental until their runtime entrypoints are made concrete. |
| bigEVY | Architecture and placeholder services exist. The large-model service simulates loading and responses; it is not a production central AI node yet. |
| enhanced lilEVY mesh mode | LoRa and smart-routing prototypes exist, but the enhanced orchestrator has model/schema/import mismatches and should be treated as experimental until repaired. |

## Start Here

- [Minimum Reader Guide](docs/EVY_MINIMUM_READER_GUIDE.md): a plain-English overview for anyone joining the project.
- [Current Codebase Analysis and Gaps](docs/CODEBASE_ANALYSIS_AND_GAPS.md): detailed review of what exists, what is broken, and what is hardware-gated.
- [BitNet Local 1-Bit LLM](docs/BITNET_LOCAL_LLM.md): local model decision, setup path, and validation notes.
- [LLM And RAG Tuning](docs/LLM_RAG_TUNING.md): retrieval/prompt evaluation harness and why training is deferred.
- [Knowledge Packs And SQLite RAG](docs/KNOWLEDGE_PACKS_AND_SQLITE_RAG.md): signed-pack manifest, optional SQLite RAG interface, and Plus Code metadata.
- [Observability](docs/OBSERVABILITY.md): metric names and optional local OpenTelemetry Collector profile.
- [Technology Opportunities](docs/TECHNOLOGY_OPPORTUNITIES.md): decision matrix for additional tech worth considering.
- [Pre-Hardware Backlog](docs/EVY_PRE_HARDWARE_BACKLOG.md): phased work items to complete before and during hardware arrival.
- [Deployment Runbook](docs/DEPLOYMENT_RUNBOOK.md): verified pre-hardware container path and hardware bring-up order.
- [First Hardware Bring-Up Runbook](docs/FIRST_HARDWARE_BRINGUP_RUNBOOK.md): exact first Pi/GSM/BitNet bench procedure.
- [Hardware Validation Checklist](docs/HARDWARE_VALIDATION_CHECKLIST.md): target validation order once hardware is available.
- [Software Validation Checklist](docs/SOFTWARE_VALIDATION_CHECKLIST.md): current software gate process.
- [Documentation Index](docs/INDEX.md): all project docs.

## What EVY Is For

EVY is designed to let a person send an SMS and receive a short useful response. The intended field version should be able to:

- Receive SMS messages through a GSM modem or HAT.
- Classify requests as emergency, command, greeting, or general query.
- Answer simple questions locally with a small model and local knowledge base.
- Retrieve local emergency and community information from an offline RAG store.
- Prioritize emergency messages.
- Share selected messages or knowledge between nodes over LoRa mesh.
- Run from a Raspberry Pi-class device with constrained memory, storage, and power.
- Optionally offload heavier work to a bigEVY central node when a network path exists.

The current repository is best understood as a software prototype and validation harness preparing for hardware bring-up, not a finished field appliance.

## What Is Available Now

### Backend Services

The Python backend includes these FastAPI services:

- `backend/services/sms_gateway/main.py`
  - Sends SMS through a queued path when Redis is available.
  - Falls back to direct send when Redis is unavailable.
  - Supports Gammu and direct serial AT-command drivers.
  - Runs in simulation mode when no GSM driver is available.
  - Provides endpoints for health, send, receive, sent/received history, queue stats, GSM status, and message parsing.

- `backend/services/message_router/main.py`
  - Classifies messages.
  - Routes to RAG and LLM services.
  - Chunks long responses into SMS-sized messages.
  - Handles simple emergency templates and operator status commands.
  - Tracks basic route statistics and overload rejections.

- `backend/services/llm_inference/main.py`
  - Supports `openai`, `ollama`, `tiny`, and `bitnet` provider modes.
  - Defaults to local BitNet b1.58 2B4T through `bitnet.cpp` for lilEVY.
  - Uses `TinyModelManager` for local/Ollama-backed tiny-model paths.
  - Reports whether the configured BitNet runtime and model file are installed.
  - Enforces short SMS-style responses.
  - Includes provider switching and tiny-model load/unload endpoints.

- `backend/services/rag_service/main.py`
  - Uses ChromaDB plus a local document manager.
  - Provides optional SQLite RAG endpoints behind `SQLITE_RAG_ENABLED=true` or `RAG_BACKEND=sqlite`.
  - Imports v1 knowledge packs through a manifest with source, expiration, checksum, and optional signature metadata.
  - Supports search, add, bulk import, export, categories, delete, embedding test, and advanced search endpoints.
  - Includes chunking, similarity filtering, and local document sync.

- `backend/services/privacy_filter/main.py`
  - Includes message validation, sanitization, rate-limit checks, consent records, blocklist operations, and audit-log endpoints.

- `backend/services/emergency_response/*`
  - Detects emergency language and produces resource-aware emergency responses.
  - Exists as a service module, but is not fully wired into the main message-router flow.

- `backend/shared/database/edge_db.py`
  - SQLite edge database with intended WAL, batching, retention, analytics, and emergency-log tables.
  - Immediate inserts, batching, stats, and retention behavior are covered by passing tests; Linux/Raspberry Pi filesystem behavior still needs hardware validation.

### Rust Services

Rust crates are present under `backend/rust_services/`:

- `sms_gateway`
- `message_router`
- `compression`

These are intended to become critical-path services or PyO3-backed modules. They now compile and pass their local tests, but they are not yet active runtime dependencies because the Python bridge in `backend/shared/integration/rust_services.py` still explicitly runs fallback behavior.

### Frontend

The frontend is a React 18, TypeScript, Vite, TailwindCSS dashboard with pages for:

- Dashboard
- Messages
- Services
- Knowledge
- Settings

The dashboard reads backend health/history/stat endpoints, but several actions and settings controls are not wired to backend mutations yet.
The Vite API base URL uses `VITE_API_URL`, with `REACT_APP_API_URL` retained as a fallback for older local env files.

### Knowledge Data

The `data/` folder contains generated local knowledge JSON files, including emergency, Wichita/local services, education, legal, community, health, cultural, technology, security, automation, analytics, and advanced-feature datasets.

Scripts under `scripts/` can build and import knowledge data, including:

- `scripts/bootstrap_knowledge_base.py`
- `scripts/import_to_rag.py`
- `scripts/build_*`
- `scripts/collect_local_data.py`

Pre-hardware knowledge-pack support is implemented in:

- `backend/services/rag_service/knowledge_pack.py`
- `backend/services/rag_service/sqlite_rag_store.py`
- `scripts/validate_knowledge_pack.py`
- `docs/KNOWLEDGE_PACKS_AND_SQLITE_RAG.md`

### Validation Assets

Software validation:

```bash
python scripts/test_software_suite.py --stage full
```

Deterministic pre-hardware SMS smoke test:

```bash
python scripts/pre_hardware_smoke.py
```

Containerized pre-hardware smoke test:

```bash
python scripts/pre_hardware_compose_smoke.py --base-port 18100
```

Hardware validation, once hardware exists:

```bash
python scripts/test_edge_hardware_suite.py \
  --gsm-device /dev/ttyUSB0 \
  --gps-device /dev/ttyAMA0 \
  --lora-frequency 915.0 \
  --power-telemetry /data/telemetry/power.json
```

Individual hardware scripts exist for GSM, LoRa, GPS, and power telemetry.
The hardware suite writes the standard artifact `data/lilevy/software_reports/hardware_validation_report.json`.

Boot self-check report scaffold:

```bash
python scripts/boot_self_check.py
```

Raspberry Pi bootstrap readiness report:

```bash
python scripts/pi_bootstrap_check.py --require-docker
```

Sample knowledge-pack validation and SQLite RAG import:

```bash
python scripts/validate_knowledge_pack.py --require-signature --import-sqlite --search "boil water"
```

LLM/RAG retrieval tuning without requiring a running model:

```bash
python scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1
```

Optional local observability collector:

```bash
docker compose -f docker-compose.observability.yml config --quiet
docker compose -f docker-compose.observability.yml up
```

## Important Gaps

These are the highest-impact gaps before hardware testing:

- Repair remaining draft bigEVY/enhanced/hybrid Dockerfiles and Compose files that reference missing modules, missing startup scripts, or missing frontend Dockerfiles.
- Fix enhanced lilEVY orchestration mismatches before treating mesh mode as runnable.
- Add real LoRa receive/IRQ handling, packet tests, and checksum validation.
- Decide whether the first hardware test is GSM-only, GSM plus local RAG/LLM, or full GSM plus LoRa.
- Add a hardware bring-up runbook with exact device paths, expected AT responses, LoRa frequency, GPIO pins, and pass/fail evidence.
- Harden secrets, API access, operator commands, phone-number policies, logging, and emergency escalation before any public or field exposure.
- Decide whether to take the breaking Vite/esbuild upgrade called out by `npm audit` or document the dev-server-only risk for the pre-hardware branch.

See [Current Codebase Analysis and Gaps](docs/CODEBASE_ANALYSIS_AND_GAPS.md) and [Pre-Hardware Backlog](docs/EVY_PRE_HARDWARE_BACKLOG.md) for the detailed breakdown.

## Target Architecture

```text
User phone
  |
  | SMS
  v
lilEVY edge node
  |
  |-- SMS gateway
  |-- Message router
  |-- Privacy filter
  |-- Emergency response logic
  |-- Local RAG / ChromaDB or optional SQLite FTS5 store
  |-- Local tiny LLM / Ollama path
  |-- SQLite edge database
  |-- Optional LoRa mesh service
  |
  | LoRa, internet, or other available link
  v
Optional bigEVY central node
  |
  |-- Larger model inference
  |-- Global RAG
  |-- Sync, analytics, model updates
```

## Repository Map

```text
EVY/
  backend/
    api_gateway/                 FastAPI gateway prototype
    services/
      sms_gateway/               SMS, GSM, parser, queue
      message_router/            Routing and response flow
      llm_inference/             OpenAI/Ollama/tiny model service
      rag_service/               ChromaDB and document manager
      privacy_filter/            Sanitization, consent, rate limits
      emergency_response/        Emergency detector and templates
    lilevy/services/             Edge-node, LoRa, local RAG/LLM prototypes
    bigevy/services/             Central-node prototype services
    shared/                      Models, config, database, integration helpers
    rust_services/               Rust SMS/router/compression crates
    tests/                       Python test suite
  frontend/                      React/Vite dashboard
  scripts/                       Knowledge builders and validation scripts
  data/                          Generated local knowledge datasets and reports
  docs/                          Architecture, plans, validation, and reviews
  monitoring/                    Prometheus configuration
  docker-compose.prehardware.yml Verified lightweight pre-hardware container profile
  docker-compose*.yml            Deployment drafts for local/lilEVY/bigEVY/hybrid modes
```

## Target Hardware

The target lilEVY node is currently:

- Raspberry Pi 5 preferred, 8 GB minimum RAM.
- 64 GB or larger microSD/SSD storage for OS, models, logs, and local knowledge.
- SIM7600-class or compatible GSM/LTE HAT for SMS.
- SX1276-class LoRa HAT using SPI and GPIO.
- GPS via UART or modem GNSS path.
- Power telemetry source exposed through a JSON file or future I2C integration.
- 50 W minimum solar panel for early testing, larger depending on measured load.
- Battery sized from measured load; the previous estimate targets roughly 12 V / 36 Ah for multi-day runtime.
- Weather-resistant enclosure, antennas, grounding, cable strain relief, and thermal planning.

Target defaults in code and validation scripts:

- GSM device: `/dev/ttyUSB0`
- GPS device: `/dev/ttyAMA0`
- LoRa SPI: `/dev/spidev0.0`
- LoRa frequency for US testing: `915.0 MHz`
- LoRa GPIO defaults: CS `25`, DIO0 `4`, reset `17`
- Power telemetry file: `/data/telemetry/power.json`
- Local LLM target: BitNet b1.58 2B4T through `bitnet.cpp`
- Local BitNet model path: `/models/bitnet/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf`
- Local BitNet runtime path: `/opt/bitnet.cpp`
- Optional SQLite RAG DB path: `/data/lilevy/sqlite_rag.db`
- Boot self-check report path: `data/lilevy/software_reports/boot_self_check_report.json`

These defaults should be confirmed against the exact HATs before hardware arrives.

## Software Requirements

Backend:

- Python 3.11 for local development.
- `pip install -r backend/requirements.txt`
- Optional local Ollama service for local LLM mode.
- Optional Redis for queued SMS mode.
- Optional ChromaDB persistence directory for RAG.
- Hardware-specific Linux packages for Gammu, serial, SPI, GPIO, and Raspberry Pi interfaces.

Frontend:

- Node.js 20 or compatible current LTS.
- `npm install` from `frontend/`
- `npm run dev` for local dashboard development.
- `npm run build` for the current frontend build gate.

Rust:

- Rust toolchain and Cargo.
- `cargo test` in each crate under `backend/rust_services/`.
- Rust crates are validated as standalone crates, but PyO3/runtime integration is still future work.

## Validation Baseline From This Review

Commands run from `C:\Users\jonat\EVY`:

```bash
python scripts/test_software_suite.py --stage full
```

Result: passed, including the pre-hardware smoke test.

```bash
python scripts/pre_hardware_smoke.py
```

Result: passed and wrote `data/lilevy/software_reports/pre_hardware_smoke_report.json`.

```bash
python -m pytest backend/tests -q
```

Result: passed with the current backend test suite.

```bash
cargo test
```

Result: passed in `sms_gateway`, `message_router`, and `compression`.

```bash
npm run build
```

Result: passed after `npm install`.

```bash
docker compose config --quiet
```

Result: passed for the main Compose configuration.

```bash
python scripts/pre_hardware_compose_smoke.py --base-port 18100
```

Result: passed for the lightweight pre-hardware Compose stack.

## Deployment Notes

Use `docker-compose.prehardware.yml` as the first verified container path. It runs the real API/SMS/router/privacy services with deterministic RAG/LLM stubs:

```bash
python scripts/pre_hardware_compose_smoke.py --base-port 18100
```

Treat `docker-compose.lilevy.yml` as the config-verified core edge-node profile. It points at real API/SMS/router/LLM/RAG/privacy modules and now passes:

```bash
docker compose -f docker-compose.lilevy.yml config --quiet
```

On Linux/Raspberry Pi hardware, `deploy-lilevy.sh` creates the runtime directories, writes `.env.lilevy`, builds the core profile, starts the services, and checks the configured health endpoints.

Before local LLM field testing, install the 1-bit runtime/model:

```bash
bash scripts/setup_bitnet_cpp.sh
```

Then capture a readiness report:

```bash
python scripts/validate_bitnet_local_llm.py --run-inference
```

Then run the SMS prompt benchmark:

```bash
python scripts/benchmark_bitnet_sms_prompts.py
```

Details are in [BitNet Local 1-Bit LLM](docs/BITNET_LOCAL_LLM.md).

Treat the main `docker-compose.yml` as the full-service deployment path under repair. It now passes:

```bash
docker compose config --quiet
```

Treat bigEVY, enhanced lilEVY, and hybrid deployment files as drafts until the pre-hardware backlog is completed.

Known draft deployment blockers include:

- `backend/Dockerfile.bigevy` references `backend.bigevy.main:app`, which does not exist.
- `docker-compose.enhanced-lilevy.yml` references `frontend/Dockerfile.enhanced-lilevy`, which does not exist.
- `backend/Dockerfile.enhanced-lilevy` starts Uvicorn against an object that is not a FastAPI app.

## Before Hardware Arrives

The recommended phase order is:

1. Keep software gates green: full Python tests, curated software suite, Rust crate tests, and frontend install/build.
2. Finish deployment gates: one runnable main Compose path, draft Dockerfile cleanup, health checks, env templates.
3. Lock hardware assumptions: HAT model, device paths, LoRa region/frequency, GPIO pins, power telemetry source.
4. Extend the simulated SMS flow from deterministic stubs to the selected local model/RAG runtime.
5. Add operator safety: secrets, phone allowlist, emergency command policy, logging, and runbook.
6. Run hardware bring-up in the order GSM, LoRa, GPS, power, integrated node.

The detailed work items are in [Pre-Hardware Backlog](docs/EVY_PRE_HARDWARE_BACKLOG.md).

## License

MIT License.

## Contact

Project contact in the existing README history: `jonathan.kershaw@gmail.com`.
