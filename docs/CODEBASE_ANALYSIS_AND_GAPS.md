# EVY Current Codebase Analysis and Gaps

This document is a current-state review of the EVY repository. It focuses on what is actually present in code, what is verified, what is experimental, and what should be completed before hardware testing begins.

## Executive Summary

EVY has a meaningful Python prototype for SMS-based AI routing, local RAG, local/tiny model inference, emergency detection, privacy filtering, and hardware validation scripts. The curated software validation suite, deterministic pre-hardware SMS smoke test, full backend pytest suite, Rust crate tests, and frontend build now pass in this workspace.

The repo is still not field-ready. The pre-hardware and core lilEVY Compose paths are now structurally valid, but bigEVY/enhanced/hybrid deployment files still describe draft runtime surfaces. The enhanced LoRa/mesh path has orchestration and data-model mismatches, and hardware-specific paths have not yet been proven on target Raspberry Pi hardware.

The most important near-term goal is to turn the current prototype into a clean deployment and hardware-assumption release candidate before hardware arrives. The Python, Rust, frontend, deterministic simulated SMS flow, pre-hardware Compose smoke, and main Compose config gates are now green; real local model/RAG runtime selection and hardware assumptions remain the next gates.

## Verification Results

These commands were run during this review from the repository root.

| Check | Result | Notes |
| --- | --- | --- |
| `python scripts/test_software_suite.py --stage full` | Pass | Curated validation steps passed, including deterministic pre-hardware smoke. |
| `python scripts/pre_hardware_smoke.py` | Pass | Normal query, `/status` command, and emergency message flowed through API gateway, privacy filter, SMS gateway, message router, stub RAG/LLM, and response history. |
| `python scripts/pre_hardware_compose_smoke.py --base-port 18100` | Pass | Lightweight Compose stack built, started healthy, passed the external smoke test, and shut down. |
| `python -m pytest backend/tests -q` | Pass | Current backend test suite passed. |
| `cargo test` in `backend/rust_services/sms_gateway` | Pass | 4 integration tests passed. |
| `cargo test` in `backend/rust_services/message_router` | Pass | 6 integration tests passed. |
| `cargo test` in `backend/rust_services/compression` | Pass | 7 integration tests passed. |
| `npm install` and `npm run build` in `frontend` | Pass | Production Vite build passes. `npm audit` still reports a moderate Vite/esbuild dev-server advisory with a breaking upgrade path. |
| `docker compose config --quiet` | Pass | Main Compose configuration parses cleanly and injects service hostnames for container networking. |
| `docker compose -f docker-compose.lilevy.yml config --quiet` | Pass | Core lilEVY service profile parses cleanly and points at real API/SMS/router/LLM/RAG/privacy modules. |

## Repository Shape

The repository has five major surfaces:

- Python backend services under `backend/`.
- Rust prototype crates under `backend/rust_services/`.
- React/Vite dashboard under `frontend/`.
- Generated knowledge data under `data/`.
- Planning, architecture, validation, and historical docs under `docs/`.

The docs are extensive, but some older docs describe intended production architecture more strongly than the current code supports. The README has been rewritten to make the current state explicit.

## Implemented Backend Surface

### API Gateway

Path: `backend/api_gateway/main.py`

What exists:

- Root endpoint.
- Gateway health endpoint.
- Aggregated service health endpoint.
- SMS send/receive proxy endpoints.
- SMS history proxy endpoint.
- Knowledge stats proxy endpoint.

Gaps:

- The gateway now consumes configurable service URL settings from `backend/shared/config.py`, so Docker can inject service hostnames.
- No authentication, API keys, operator role model, or rate limiting at the gateway layer.
- Error handling assumes downstream responses are JSON and does not preserve downstream status codes.

### SMS Gateway

Path: `backend/services/sms_gateway/main.py`

What exists:

- FastAPI service for SMS send, receive, health, GSM status, queue stats, queue cleanup, GSM reconnect, and message parsing.
- Gammu driver and direct serial AT-command driver.
- Redis-backed queue with direct-send fallback when Redis is unavailable.
- Bounded inbound queue and retry forwarding to the message router.
- In-memory dead-letter list for router-forward failures.
- Simulation mode if no GSM driver initializes.
- Direct-send simulation responses are now recorded in sent history.

Gaps:

- Sent message history is stored in memory but is not consistently appended during successful sends.
- Direct serial receive support is limited compared with send support.
- Rate limiting is minimal and currently based on last-send timestamp per receiver.
- In-memory received/sent history and dead-letter buffers are not durable.
- Hardware behavior is unproven until a real modem, SIM, antennas, and carrier conditions are tested.

### Message Router

Path: `backend/services/message_router/main.py`

What exists:

- Message classification using parsed SMS metadata or fallback keyword logic.
- Routing to RAG and LLM services.
- SMS chunking for long responses.
- Simple emergency handling.
- Basic command handling, including `!status`/`/status`.
- LLM inflight semaphore and overload response.
- Service status checks.
- Explicit operator commands now override upstream `unknown` parser metadata, so `/status` remains a command in the simulated end-to-end path.

Gaps:

- Emergency response uses local simple templates instead of the richer emergency response service module.
- Privacy filtering happens at the API gateway, not consistently inside router-level direct calls.
- Commands are not authenticated.
- Weather and news commands are placeholders.
- No durable workflow record for routed messages, failures, or emergency events.

### LLM Inference

Paths:

- `backend/services/llm_inference/main.py`
- `backend/services/llm_inference/tiny_model_manager.py`
- `backend/services/llm_inference/edge_model_manager.py`

What exists:

- Provider modes for `openai`, `ollama`, `tiny`, and `bitnet`.
- Native BitNet b1.58 2B4T adapter through `bitnet.cpp`.
- Tiny model registry including TinyLlama, DialoGPT-small, DistilGPT2, and BitNet compatibility entries.
- Ollama integration.
- Transformers fallback.
- Model load/unload endpoints.
- Memory and inflight limits.

Gaps:

- BitNet runtime/model setup is now explicit, but it is not yet measured on target Raspberry Pi hardware.
- The Docker path assumes `bitnet.cpp` has been prepared under `third_party/BitNet` and mounted into the container.
- No measured BitNet cold-start, latency, memory, or power profile on target hardware yet.

### RAG Service

Paths:

- `backend/services/rag_service/main.py`
- `backend/services/rag_service/document_manager.py`
- `backend/services/rag_service/embedding_service.py`

What exists:

- ChromaDB persistent collection.
- Local document manager.
- Local embedding service and simple fallback embedding service.
- Hybrid search combining vector and text results.
- Similarity thresholding.
- Document add, bulk-add, delete, import, export, categories, advanced search, and embedding test endpoints.
- Chunking and content-hash sync behavior.

Gaps:

- ChromaDB vector search uses Chroma's `query_texts` path and does not clearly use the custom local embedding service for collection embeddings.
- Frontend knowledge stats expect a flatter shape than `rag_service.get_stats()` returns.
- Knowledge data currency, provenance, and update policy need review before emergency or public use.
- Import paths and local document directories need a hardware-ready convention.

### Privacy Filter

Path: `backend/services/privacy_filter/main.py`

What exists:

- Message validation.
- Text sanitization.
- Rate-limit checks.
- Consent record management.
- Blocklist endpoints.
- Audit log endpoint.

Gaps:

- No durable consent/audit persistence is evident from the high-level service surface.
- No authentication around sensitive privacy/admin endpoints.
- Needs integration testing in every ingress path, not only API gateway receive.

### Emergency Response

Paths:

- `backend/services/emergency_response/detector.py`
- `backend/services/emergency_response/service.py`
- `backend/services/emergency_response/templates.py`

What exists:

- Pattern-based emergency detection.
- Emergency type and severity classification.
- Emergency response templates.
- Resource-aware response compression/truncation.
- Local emergency contact support.

Gaps:

- Not fully wired into the main router flow.
- No field-approved emergency wording, escalation rules, or agency integration.
- Emergency logs need durable persistence and operator review workflow.

### Edge Database

Path: `backend/shared/database/edge_db.py`

What exists:

- SQLite schema for messages, analytics, and emergency logs.
- Intended WAL mode, batching, retention, indexes, and database stats.

Gaps:

- Immediate inserts now commit and are covered by passing tests.
- Memory-mapped I/O PRAGMA behavior was normalized for this test environment, but should still be verified on Linux/Raspberry Pi storage.
- Needs Linux/Raspberry Pi validation because SQLite PRAGMA behavior can differ by platform and filesystem.

## Rust Services Review

Rust crates exist for intended critical-path performance. They now compile and pass local tests, but they are not wired into the active Python runtime path.

### SMS Gateway Crate

Path: `backend/rust_services/sms_gateway`

Current status:

- `cargo test` passes.
- The crate exposes core queue types at the crate root for integration-test and consumer ergonomics.
- The `python` feature is declared, but PyO3 integration still needs a dedicated validation pass before runtime use.

### Message Router Crate

Path: `backend/rust_services/message_router`

Current status:

- `cargo test` passes.
- Command classification now treats explicit slash commands such as `/help` as commands before emergency keyword matching.
- The `python` feature is declared, but PyO3 integration still needs a dedicated validation pass before runtime use.

### Compression Crate

Path: `backend/rust_services/compression`

Current status:

- `cargo test` passes.
- Compression statistics update without the previous numeric type mismatch.
- The `python` feature is declared, but PyO3 integration still needs a dedicated validation pass before runtime use.

### Python Bridge

Path: `backend/shared/integration/rust_services.py`

Current state:

- `RUST_SERVICES_AVAILABLE = False`.
- PyO3 imports are commented out.
- Wrappers return fallback behavior and placeholder stats.

Conclusion:

The README should describe Rust services as standalone-tested components, not active production components, until they expose validated Python bindings and are used by the runtime path.

## LoRa, Mesh, and Enhanced lilEVY Review

Paths:

- `backend/lilevy/services/lora_radio_service.py`
- `backend/shared/communication/smart_router.py`
- `backend/lilevy/services/enhanced_lilevy_service.py`

What exists:

- LoRa message dataclass, node info, routing table, discovery loop, message queue, and simulated hardware mode.
- SPI/GPIO setup path for SX1276-class radios.
- GPS and power telemetry helper paths.
- Smart routing policies across SMS, LoRa, internet, and Bluetooth layers.

Gaps:

- LoRa checksum calculation includes the checksum field, which can make verification fail after a checksum is set.
- Hardware transmit path writes bytes over SPI but does not implement a complete SX1276 packet transmit/receive state machine.
- Receive path is based on an internal list, not real DIO0/IRQ packet reception.
- Internet availability check imports `aiohttp`, but `aiohttp` is not in `backend/requirements.txt`.
- Enhanced lilEVY service references `MessageType` and `MessagePriority` without importing them in all needed scopes.
- Enhanced lilEVY service imports `llm_inference_engine`, but the LLM module exposes `llm_engine`.
- Enhanced lilEVY service builds `SMSMessage` with `phone_number`, but the shared model requires `sender`, `receiver`, and `content`.
- Enhanced lilEVY service uses `LLMRequest(max_tokens=...)`, but the shared model uses `max_length`.
- Enhanced lilEVY service creates `ServiceHealth(status=..., message=...)`, but the shared model requires `service_name`, `status`, and `version`.

Conclusion:

Mesh mode is a prototype. It should be repaired and validated separately from the first GSM/local-RAG hardware milestone.

## bigEVY Review

Paths:

- `backend/bigevy/services/large_llm_service.py`
- `backend/bigevy/services/global_rag_service.py`
- `backend/shared/communication/node_client.py`

What exists:

- Deployment profile for bigEVY.
- Placeholder large-model manager.
- Simulated large-model loading and response generation.
- Global RAG and sync concepts.

Gaps:

- No `backend/bigevy/main.py`, despite Dockerfile references.
- Large model generation is simulated.
- No real GPU runtime validation.
- No production load balancer, sync API, or model update service is implemented.

Conclusion:

bigEVY is an architecture direction and prototype surface, not an available central node.

## Frontend Review

Path: `frontend/`

What exists:

- React/Vite/Tailwind dashboard.
- Pages for dashboard, messages, services, knowledge, and settings.
- React Query and Axios integration for health/history/stats endpoints.

Gaps:

- Local build passes after `npm install`.
- The frontend now reads `VITE_API_URL` first and keeps `REACT_APP_API_URL` as a fallback.
- `package.json` has a `lint` script using ESLint, but ESLint is not listed in dev dependencies.
- Settings form does not persist changes.
- Knowledge actions are display-only.
- Dashboard metrics include static placeholder values.
- `npm audit` reports a moderate Vite/esbuild dev-server advisory. The suggested automated fix upgrades to Vite 8 and should be handled as an intentional dependency-upgrade task.

## Deployment Review

Deployment files exist for pre-hardware, standard, lilEVY, enhanced lilEVY, bigEVY, and hybrid modes. The pre-hardware Compose file builds and passes a container smoke test. The core lilEVY Compose file now uses real service entrypoints and passes config validation. The main, bigEVY, enhanced lilEVY, and hybrid Compose files also parse cleanly. bigEVY/enhanced/hybrid still need runtime-entrypoint cleanup before hardware testing.

Verified path:

- `docker-compose.prehardware.yml`
- `Dockerfile.prehardware`
- `backend/requirements-prehardware.txt`
- `scripts/pre_hardware_compose_smoke.py`

Core lilEVY config-verified path:

- `docker-compose.lilevy.yml`
- `backend/Dockerfile.lilevy`

Confirmed blockers:

- `backend/Dockerfile.bigevy` references `backend.bigevy.main:app`; that file does not exist.
- `docker-compose.enhanced-lilevy.yml` references `frontend/Dockerfile.enhanced-lilevy`; that file does not exist.
- `backend/Dockerfile.enhanced-lilevy` starts Uvicorn against `enhanced_lilevy_service`, which is a service object, not a FastAPI `app`.
- bigEVY/enhanced/hybrid Compose files still declare services whose app entrypoints are not implemented.

## Hardware Readiness

Hardware-related code paths and scripts are present:

- GSM AT validation: `scripts/test_gsm_hardware.py`
- LoRa SPI/GPIO validation: `scripts/test_lora_hardware.py`
- GPS NMEA validation: `scripts/test_gps_hardware.py`
- Power telemetry validation: `scripts/test_power_hardware.py`
- Combined suite: `scripts/test_edge_hardware_suite.py`
- Checklist: `docs/HARDWARE_VALIDATION_CHECKLIST.md`

Hardware is not yet validated. Before hardware arrives, the team should finalize:

- Exact Raspberry Pi model and OS image.
- GSM HAT model, modem chipset, carrier/SIM plan, antennas, and expected serial device map.
- LoRa HAT model, frequency band, antenna, SPI bus, CS/DIO/reset pins, and legal regional settings.
- GPS source and device path.
- Power telemetry source and format.
- Initial no-internet, no-Redis, and reboot behavior expectations.

## Priority Gap List

### P0 - Must fix before hardware testing

- Real local model/RAG runtime selection beyond deterministic smoke stubs.
- Hardware device-path and HAT mapping.

### P1 - Should fix before first integrated field-style run

- Enhanced lilEVY schema/import issues.
- LoRa checksum and real packet receive/transmit implementation.
- Emergency response service integration into router.
- Durable message, emergency, and dead-letter persistence.
- Frontend lint setup and dependency-audit decision.
- Secrets and operator command policy.

### P2 - Can follow initial hardware bring-up

- bigEVY real model runtime.
- Multi-node mesh routing.
- Knowledge content management.
- Analytics dashboards.
- CI/CD automation.
- Multi-language support.

## Recommended Release Gates

Before touching hardware:

- `python -m pytest backend/tests -q` stays green.
- `python scripts/test_software_suite.py --stage full` stays green.
- All Rust crates under `backend/rust_services/` pass `cargo test`.
- Frontend can run `npm install` and `npm run build`.
- Main Compose config passes `docker compose config --quiet`.
- Core lilEVY Compose config passes `docker compose -f docker-compose.lilevy.yml config --quiet`.
- Lightweight pre-hardware Compose stack passes `python scripts/pre_hardware_compose_smoke.py --base-port 18100`.
- A deterministic local simulated SMS request can go API gateway -> privacy filter -> SMS gateway -> message router -> RAG/LLM stubs -> SMS gateway.
- A real local model/RAG simulated run is selected and documented if it is required for the first hardware milestone.
- Docker or non-Docker local runbook has one supported path that works from a clean checkout.

First day with hardware:

- GSM script passes AT, SIM, registration, and signal checks.
- One SMS send and one SMS receive are manually confirmed.
- LoRa script passes SPI/GPIO reset checks.
- GPS script sees NMEA and records a fix when a GPS source is expected.
- Power script reads a valid battery level.
- Integrated node records a JSON report and operator notes.
