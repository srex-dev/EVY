# EVY Minimum Reader Guide

This is the shortest practical explanation of EVY for someone who has not read the rest of the repo.

## What EVY Is

EVY is a project to build a small SMS-based AI assistant that can run near the edge of a community network. A person sends a text message, EVY reads it, decides what kind of request it is, and sends back a short useful answer.

The long-term goal is a field node that can keep helping during weak internet, outages, or emergency conditions.

## The Two Node Types

`lilEVY` is the small edge node.

- Runs on Raspberry Pi-class hardware.
- Talks to users by SMS.
- Uses local knowledge and the BitNet b1.58 2B4T local LLM when possible.
- May use LoRa radio to talk to nearby EVY nodes.
- Should be able to run with limited power.

`bigEVY` is the optional central node.

- Runs on larger server hardware.
- Can host larger models and a bigger knowledge base.
- Can help lilEVY nodes when internet or mesh paths are available.
- Is currently mostly prototype/placeholder in this repo.

## What Works Today

The repo currently has:

- Python backend services for SMS gateway, message routing, local LLM inference, RAG search, privacy filtering, emergency detection, and edge storage.
- A React dashboard prototype.
- Generated local knowledge datasets.
- Hardware validation scripts for GSM, LoRa, GPS, and power telemetry.
- Docker and deployment drafts.
- A curated software validation suite that passes.
- A full backend Python test suite that passes.
- Rust service crates that compile and pass their local tests.
- A frontend dashboard that installs and builds.
- A deterministic pre-hardware SMS smoke test that proves normal query, command, and emergency flows without hardware.
- A lightweight pre-hardware Docker Compose path that starts the same simulated flow in containers.
- A configured local 1-bit LLM path using BitNet b1.58 2B4T through `bitnet.cpp`.
- A v1 knowledge-pack manifest validator and optional SQLite FTS5 RAG store behind a feature flag.
- Plus Code parsing for SMS location metadata.
- A boot self-check report scaffold that separates missing hardware from simulation mode.

## What Is Not Ready Yet

The system is not field-ready.

Before hardware testing, these need attention:

- bigEVY, enhanced, and hybrid deployment profiles still need runtime hardening even though their Compose files parse.
- LoRa mesh mode is still experimental.
- bigEVY large-model behavior is simulated.
- BitNet has not been measured on the target Raspberry Pi hardware yet.
- The frontend has a Vite/esbuild audit finding that should be handled deliberately as a dependency-upgrade task.
- The React dashboard still has display-only actions and settings.
- Real GSM, LoRa, GPS, and power hardware have not been validated.

## Minimum Hardware Target

For the first practical lilEVY hardware test:

- Raspberry Pi 5 with 8 GB RAM.
- 64 GB or larger storage.
- GSM/LTE HAT or modem that supports SMS.
- SIM card with SMS service.
- Antenna for cellular.
- SX1276-class LoRa HAT for mesh testing.
- LoRa antenna matched to the legal local frequency.
- GPS source if location is part of the test.
- Power telemetry source, even if it starts as a simple JSON file.
- Local BitNet model storage for `bitnet-b1.58-2B-4T`.
- Reliable 5 V power supply for bench testing before solar.

Solar, enclosure, battery, and weatherproofing should come after the bench software and modem tests are reliable.

## Minimum Software Target

Before hardware arrives, the software should prove:

- A test SMS object can enter the API.
- The privacy filter accepts or rejects it.
- The SMS gateway parses it.
- The router classifies it.
- RAG or LLM produces a short answer.
- Optional SQLite RAG can import and search a sample knowledge pack.
- Long answers are chunked to SMS-sized messages.
- Emergency messages are prioritized.
- Plus Code location metadata is preserved when users include it in SMS.
- Failures are logged and visible.

## The Most Important Commands

Run the curated software validation suite:

```bash
python scripts/test_software_suite.py --stage full
```

Run the deterministic pre-hardware smoke test:

```bash
python scripts/pre_hardware_smoke.py
```

Run the containerized pre-hardware smoke test:

```bash
python scripts/pre_hardware_compose_smoke.py --base-port 18100
```

Prepare the local BitNet LLM on Linux/Raspberry Pi:

```bash
bash scripts/setup_bitnet_cpp.sh
```

Run the full Python tests:

```bash
python -m pytest backend/tests -q
```

Run the knowledge-pack, SQLite RAG, Plus Code, and boot self-check tests:

```bash
python -m pytest backend/tests/test_knowledge_pack.py backend/tests/test_knowledge_pack_script.py backend/tests/test_sqlite_rag_store.py backend/tests/test_observability_and_boot.py backend/tests/test_sms_gateway.py -q
```

Validate the sample knowledge pack and prove SQLite RAG import/search:

```bash
python scripts/validate_knowledge_pack.py --require-signature --import-sqlite --search "boil water"
```

Write a local boot self-check report:

```bash
python scripts/boot_self_check.py
```

```bash
cd frontend
npm install
npm run build
```

Run in each Rust crate:

```bash
cargo test
```

When hardware arrives:

```bash
python scripts/test_edge_hardware_suite.py
```

## First Hardware Test Order

Do not start with the whole system at once. Test in this order:

1. Boot Raspberry Pi and confirm OS, Python, serial, SPI, and GPIO access.
2. Test GSM modem with AT commands.
3. Send one outbound SMS.
4. Receive one inbound SMS.
5. Test LoRa SPI/GPIO wiring.
6. Test GPS NMEA data if GPS is installed.
7. Test power telemetry.
8. Run the integrated SMS -> router -> response flow.
9. Record all results in JSON reports and notes.

## Plain-English Project Status

EVY has a real software foundation, but it is still in the "make the prototype honest and testable" stage. The next best move is not adding more features. The next best move is making the existing system pass clean software gates and then bringing up hardware one device at a time.
