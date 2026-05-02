# EVY Pre-Hardware Backlog

This backlog is organized to get EVY phase-complete before hardware arrives, then to guide the first hardware validation pass. The goal is to avoid discovering software, deployment, and documentation issues on the same day as modem and radio bring-up.

## Phase Gates

| Phase | Goal | Exit gate |
| --- | --- | --- |
| Phase 0 | Freeze current scope and assumptions | README, minimum guide, analysis, and backlog are current. Hardware assumptions are listed. |
| Phase 1 | Make software tests honest | Curated suite, full Python suite, Rust crate tests, and frontend build pass. |
| Phase 2 | Make one deployment path real | One local and one lightweight Docker runbook work from a clean checkout. |
| Phase 3 | Prove simulated end-to-end flow | Simulated SMS requests receive valid SMS-sized responses with logs and report evidence. |
| Phase 4 | Prepare hardware adapters | GSM, LoRa, GPS, and power scripts have exact expected inputs and outputs. |
| Phase 5 | Add operator safety | Secrets, phone policy, emergency policy, logging, and runbook are ready. |
| Phase 6 | Bring up hardware | Device-level hardware reports are captured and reviewed. |

## Phase 0 - Scope and Readiness

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH0-001 | P0 | Confirm first hardware milestone scope | Written decision: GSM-only, GSM plus local RAG/LLM, or GSM plus LoRa. |
| EVY-PH0-002 | P0 | Finalize target HAT list | Exact GSM, LoRa, GPS, and power telemetry devices are documented with links/specs. |
| EVY-PH0-003 | P0 | Lock device path assumptions | Expected `/dev/tty*`, `/dev/spidev*`, GPIO pins, and fallback env vars are documented. |
| EVY-PH0-004 | P1 | Choose one supported local run mode | Decide whether pre-hardware validation uses bare Python processes, Docker Compose, or both. |
| EVY-PH0-005 | P1 | Archive historical docs as historical where needed | Older docs that overstate readiness are labeled or superseded by current README/gap docs. |
| EVY-PH0-006 | P0 | Lock local LLM target | BitNet b1.58 2B4T through `bitnet.cpp` is documented as the target local LLM. |

## Phase 1 - Software Gate Repair

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH1-001 | P0 | Fix edge database immediate commits | `test_insert_message`, `test_insert_analytics`, `test_insert_emergency_log`, stats, and phone filters pass. |
| EVY-PH1-002 | P0 | Fix edge database test/import issue | `test_batch_commit_loop` no longer fails due missing `asyncio`. |
| EVY-PH1-003 | P1 | Decide mmap behavior by platform | SQLite mmap test either passes on target Linux or is skipped/adjusted for unsupported platforms. |
| EVY-PH1-004 | P0 | Fix edge model low-battery async behavior | `update_battery_level(20)` does not call `asyncio.create_task` without a running loop. |
| EVY-PH1-005 | P1 | Fix tornado emergency response template | Tornado emergency test passes and wording is reviewed for safety. |
| EVY-PH1-006 | P0 | Make full backend tests pass | `python -m pytest backend/tests -q` passes. |
| EVY-PH1-007 | P0 | Fix Rust SMS gateway compile failures | `cargo test` passes in `backend/rust_services/sms_gateway`. |
| EVY-PH1-008 | P0 | Fix Rust message router compile failures | `cargo test` passes in `backend/rust_services/message_router`. |
| EVY-PH1-009 | P0 | Fix Rust compression compile failures | `cargo test` passes in `backend/rust_services/compression`. |
| EVY-PH1-010 | P1 | Decide Rust release role | README and validation gate state whether Rust is required for first hardware milestone. |
| EVY-PH1-011 | P1 | Restore frontend build | `npm install` and `npm run build` pass in `frontend/`. |
| EVY-PH1-012 | P2 | Repair frontend lint setup | Either add ESLint dependencies/config or remove/update the broken lint script. |
| EVY-PH1-013 | P2 | Decide frontend dependency-audit path | Decide whether to take the breaking Vite/esbuild upgrade from `npm audit` before hardware, or document the dev-server-only risk for the pre-hardware branch. |

Phase 1 status: EVY-PH1-001 through EVY-PH1-011 are complete in the current workspace. EVY-PH1-012 and EVY-PH1-013 remain as non-blocking cleanup unless the team wants lint and dependency-audit policy included in the first pre-hardware release gate.

## Phase 2 - Deployment Gate

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH2-001 | P0 | Fix `backend/Dockerfile.lilevy` entrypoint | Dockerfile references an existing module/app or uses service-specific commands. |
| EVY-PH2-002 | P0 | Fix `backend/Dockerfile.bigevy` entrypoint | Dockerfile no longer references missing `backend.bigevy.main:app`. |
| EVY-PH2-003 | P0 | Remove or create missing startup scripts | `start-lilevy.sh` references are resolved. |
| EVY-PH2-004 | P0 | Fix enhanced frontend Dockerfile reference | `docker-compose.enhanced-lilevy.yml` no longer references a missing frontend Dockerfile. |
| EVY-PH2-005 | P0 | Fix API gateway service URLs in containers | Gateway uses service hostnames or env-configurable URLs in Docker. |
| EVY-PH2-006 | P1 | Normalize service port map | README, env template, compose files, and settings agree on ports. |
| EVY-PH2-007 | P1 | Add health checks for real endpoints | Compose health checks call endpoints that exist and reflect readiness. |
| EVY-PH2-008 | P1 | Create one clean local runbook | A developer can start the minimum services from a clean checkout and run a test request. |
| EVY-PH2-009 | P2 | Remove duplicated/conflicting env vars | Compose files do not repeat or contradict service URLs. |
| EVY-PH2-010 | P1 | Prepare BitNet setup path | `scripts/setup_bitnet_cpp.sh` creates the runtime/model layout and `.env.bitnet`. |

Phase 2 status: EVY-PH2-001, EVY-PH2-003, EVY-PH2-005, EVY-PH2-007, EVY-PH2-008, and EVY-PH2-010 are complete for the lightweight pre-hardware and core lilEVY paths. `docker compose config --quiet` passes for the main Compose file, `docker compose -f docker-compose.lilevy.yml config --quiet` passes for the core lilEVY profile, and `python scripts/pre_hardware_compose_smoke.py --base-port 18100` proves a containerized simulated request flow. EVY-PH2-002 and EVY-PH2-004 remain open for the bigEVY/enhanced deployment drafts. EVY-PH2-006 and EVY-PH2-009 remain partially open until env templates and all profile ports are normalized.

## Phase 3 - Simulated End-to-End Flow

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH3-001 | P0 | Define canonical simulated SMS request | One JSON request is documented for normal query, command, and emergency flow. |
| EVY-PH3-002 | P0 | Prove API gateway receive path | API gateway -> privacy filter -> SMS gateway works locally. |
| EVY-PH3-003 | P0 | Prove router response path | SMS gateway -> message router -> RAG/LLM -> SMS gateway send path works. |
| EVY-PH3-004 | P0 | Ensure response history is visible | Sent and received history endpoints show the simulated exchange. |
| EVY-PH3-005 | P1 | Integrate emergency response service | Router uses the richer emergency service module or docs state why it does not. |
| EVY-PH3-006 | P1 | Add durable dead-letter evidence | Router-forward failures are inspectable beyond an in-memory list. |
| EVY-PH3-007 | P1 | Test no-Redis fallback | SMS direct-send fallback is validated and documented. |
| EVY-PH3-008 | P1 | Test no-internet local behavior | Local RAG/LLM mode does not try to download required assets during the test. |
| EVY-PH3-009 | P2 | Add latency/report artifact | Simulated run writes timing and pass/fail evidence. |
| EVY-PH3-010 | P1 | Add BitNet readiness validation | `python scripts/validate_bitnet_local_llm.py` reports runtime/model presence, and `--run-inference` proves a local model response once assets are installed. |
| EVY-PH3-011 | P1 | Add BitNet SMS prompt benchmark | `python scripts/benchmark_bitnet_sms_prompts.py` records p50/p95 latency and SMS-sized response checks for 20 prompts. |

Phase 3 status: EVY-PH3-001 through EVY-PH3-004, EVY-PH3-009, the validation-script portion of EVY-PH3-010, and the benchmark-script portion of EVY-PH3-011 are complete. EVY-PH3-005 through EVY-PH3-008 remain open. EVY-PH3-010 and EVY-PH3-011 remain open for the first successful runtime reports after BitNet assets are installed on Linux/Raspberry Pi.

## Phase 4 - Hardware Adapter Preparation

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH4-001 | P0 | GSM AT command checklist | Expected `AT`, `AT+CPIN?`, `AT+CREG?`, and `AT+CSQ` responses are documented. |
| EVY-PH4-002 | P0 | GSM send/receive smoke test | Script or runbook sends and receives one SMS with operator confirmation. |
| EVY-PH4-003 | P0 | LoRa checksum fix | Checksum validation passes for a sent/received LoRa message object. |
| EVY-PH4-004 | P0 | LoRa packet TX/RX plan | Decide whether first LoRa test is register-level, single-node TX, or two-node TX/RX. |
| EVY-PH4-005 | P1 | SX1276 register implementation review | Register configuration is verified against chosen HAT datasheet. |
| EVY-PH4-006 | P1 | Real LoRa receive path | DIO0/IRQ or polling receive path is implemented or explicitly postponed. |
| EVY-PH4-007 | P1 | GPS path confirmation | GPS source and baud are confirmed for the chosen hardware. |
| EVY-PH4-008 | P1 | Power telemetry format | `/data/telemetry/power.json` schema is documented and sample file is provided. |
| EVY-PH4-009 | P2 | Hardware simulation flags | Simulation mode is controlled consistently with env vars and visible in health output. |

## Phase 5 - Operator Safety and Field Hygiene

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH5-001 | P0 | Secrets policy | No production secret defaults remain in deployable env files. |
| EVY-PH5-002 | P0 | Operator command policy | `!status` and admin-style commands have allowlist/auth behavior or are disabled for public numbers. |
| EVY-PH5-003 | P0 | Emergency wording review | Emergency responses are reviewed for safety, jurisdiction, and "call 911" expectations. |
| EVY-PH5-004 | P1 | Phone-number privacy policy | Retention, masking, audit, and export rules are documented. |
| EVY-PH5-005 | P1 | Logging and report paths | Software and hardware reports have stable locations and operator instructions. |
| EVY-PH5-006 | P1 | Backup/restore plan | RAG data, SQLite data, and reports can be backed up and restored. |
| EVY-PH5-007 | P2 | Observability dashboard | Minimum Prometheus/Grafana or log-based status view is available. |

## Phase 6 - Hardware Arrival Bring-Up

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH6-001 | P0 | Raspberry Pi base image setup | OS, Python, system packages, SPI/UART, and permissions are configured. |
| EVY-PH6-002 | P0 | GSM hardware validation | `scripts/test_gsm_hardware.py` passes and one real SMS send/receive is confirmed. |
| EVY-PH6-003 | P0 | LoRa wiring validation | `scripts/test_lora_hardware.py` passes for SPI/GPIO checks. |
| EVY-PH6-004 | P1 | GPS validation | `scripts/test_gps_hardware.py` sees NMEA and records a fix if GPS is installed. |
| EVY-PH6-005 | P1 | Power telemetry validation | `scripts/test_power_hardware.py` reads valid battery telemetry. |
| EVY-PH6-006 | P0 | Integrated node smoke test | One inbound SMS gets one valid EVY response through the local stack. |
| EVY-PH6-007 | P1 | One-hour modem stability run | GSM modem does not lock up during repeated send/receive checks. |
| EVY-PH6-008 | P1 | Baseline measurements | Record CPU, memory, temperature, power draw, response latency, and message reliability. |
| EVY-PH6-009 | P2 | Go/no-go review | Hardware report, logs, and known issues are reviewed before field-style testing. |

## Phase 7 - Technology Evaluation

These items should not block first hardware bring-up unless the project explicitly changes scope. Use [Technology Opportunities](TECHNOLOGY_OPPORTUNITIES.md) as the decision matrix.

| ID | Priority | Work item | Acceptance criteria |
| --- | --- | --- | --- |
| EVY-PH7-001 | P1 | Prototype SQLite RAG store | SQLite FTS5 plus sqlite-vec spike can import a small knowledge pack and answer the benchmark prompt set. |
| EVY-PH7-002 | P1 | Design signed knowledge-pack manifest | Manifest schema, expiration policy, checksums, and signing approach are documented. |
| EVY-PH7-003 | P1 | Hardware watchdog plan | Pi watchdog, systemd watchdog, read-only root, and writable data paths are documented for first hardware cycle. |
| EVY-PH7-004 | P2 | OpenTelemetry local profile | Lightweight Collector profile captures logs/metrics locally without requiring cloud export. |
| EVY-PH7-005 | P2 | Meshtastic spike plan | Decide hardware, payload format, and test success criteria for a post-GSM LoRa mesh spike. |
| EVY-PH7-006 | P2 | NATS JetStream queue spike | Compare Redis queue versus JetStream for SMS/event durability and replay. |
| EVY-PH7-007 | P2 | OTA update architecture decision | Choose RAUC, Mender, or postponed manual update path before field deployment. |
| EVY-PH7-008 | P3 | Plus Code parser | SMS parser recognizes Plus Codes and preserves normalized location metadata. |
| EVY-PH7-009 | P3 | Syncthing artifact sync policy | Only immutable reports/knowledge packs are allowed; active DB and secret sync are explicitly blocked. |
| EVY-PH7-010 | P3 | whisper.cpp operator concept | Operator-console speech-to-text use case is documented separately from lilEVY core scope. |

Phase 7 status: EVY-PH7-001 has a v1 SQLite FTS5 implementation behind a feature flag, with sqlite-vec reported in health when available but vector search still open. A repo sample pack and `scripts/validate_knowledge_pack.py --require-signature --import-sqlite --search "boil water"` prove import/search and write a report. `scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1` now proves seven retrieval tuning cases without requiring a running model, and `--require-llm` is ready for real BitNet prompt scoring. EVY-PH7-002 has a v1 knowledge-pack manifest validator/import path, while real signature verification remains open. EVY-PH7-003 has a boot self-check report scaffold, but Raspberry Pi watchdog, systemd watchdog, and read-only-root setup remain hardware-cycle work. The hardware suite now targets the standard `data/lilevy/software_reports/hardware_validation_report.json` artifact. EVY-PH7-004 has stable metric names and an optional local Collector profile, but deeper service instrumentation and dashboards remain open. EVY-PH7-008 is complete for parser metadata and tests.

## Suggested Milestone Order

1. Software Release Candidate 0: full Python tests pass, Rust crate tests pass, frontend builds, docs current.
2. Software Release Candidate 1: lightweight pre-hardware deployment path works.
3. Simulated Node Candidate: local end-to-end SMS flow works without hardware.
4. Bench Hardware Candidate: GSM works on Pi with a real SIM and antenna.
5. Radio Candidate: LoRa wiring and packet path validated.
6. Integrated Hardware Candidate: all device reports and one SMS response flow pass.

## Backlog Notes

- Keep the first hardware milestone intentionally small.
- Do not make bigEVY or full mesh routing a blocker for the first GSM/local response test unless the project explicitly chooses that scope.
- Every hardware test should produce a report artifact and human notes.
- Any simulated behavior should be visible in health output so nobody mistakes simulation for live hardware.
