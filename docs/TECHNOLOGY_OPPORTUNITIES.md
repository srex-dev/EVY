# EVY Technology Opportunities

This document captures additional technologies that could strengthen EVY. It is intentionally a decision aid, not a commitment to add every tool.

The main principle: pre-hardware work should reduce field risk. A technology is worth adding before hardware only if it improves reliability, observability, local operation, or testability without making bring-up harder.

## Recommendation Summary

| Rank | Technology | Recommendation | Timing | Why |
| --- | --- | --- | --- | --- |
| 1 | SQLite FTS5 plus sqlite-vec | v1 prototype implemented | Pre-hardware or first hardware cycle | Simplifies local RAG into one inspectable SQLite store. |
| 2 | Signed knowledge packs | v1 manifest implemented | Pre-hardware | Prevents stale or untrusted local emergency data from becoming a safety issue. |
| 3 | Hardware watchdog and read-only root | Plan now, implement on Pi | First hardware cycle | Protects against hangs and storage corruption during power loss. |
| 4 | OpenTelemetry Collector | Metric names added; collector later | Pre-hardware or first hardware cycle | Gives a standard path for local logs, metrics, traces, and later export. |
| 5 | Meshtastic | Spike, do not replace current LoRa work yet | After single-node hardware bring-up | Provides a proven off-grid LoRa mesh layer faster than custom mesh routing. |
| 6 | NATS JetStream | Spike only if Redis queue grows more complex | After current SMS path stabilizes | Durable at-least-once event flow for SMS and emergency events. |
| 7 | OTA updates with RAUC or Mender | Decide architecture | Before field deployment, not before bench tests | Safe rollback matters once nodes leave the bench. |
| 8 | Plus Codes | Parser support implemented | Early, low risk | SMS-friendly offline location references. |
| 9 | Syncthing | Use only for immutable files/reports | Later | Helpful for reports and knowledge packs, risky for active DBs. |
| 10 | whisper.cpp | Keep as operator-side optional feature | Later | Useful for operator notes, not core SMS node function. |

## 1. SQLite FTS5 Plus sqlite-vec

Implementation status: `backend/services/rag_service/sqlite_rag_store.py` now provides `import_pack(pack_path)`, `search(query, top_k)`, and `health()`. It uses SQLite FTS5 today and reports whether `sqlite-vec` is importable, while vector-table wiring remains future work.

Current EVY RAG uses Chroma-style service behavior. That is useful for prototyping, but a field node benefits from fewer services and easier inspection.

`sqlite-vec` is a small SQLite vector-search extension that runs anywhere SQLite runs, including Raspberry Pis. Its README describes pure C, no dependency vector search through `vec0` virtual tables, with float, int8, and binary vectors.

What EVY would gain:

- One-file local knowledge store.
- Easier backup, diff, sync, and recovery.
- Hybrid keyword plus vector search: SQLite FTS5 for exact terms, sqlite-vec for semantic retrieval.
- Better alignment with the existing edge SQLite database.
- Simpler disaster-node debugging: inspect with normal SQLite tools.

Suggested first spike:

- Create `backend/services/rag_service/sqlite_rag_store.py`.
- Store documents, chunks, metadata, source, expiration, and embedding.
- Support `search(query, top_k)` with FTS-only fallback if vector extension is unavailable.
- Add a benchmark against the current RAG service using 20 emergency prompts.

Decision: pre-hardware v1 prototype is implemented behind `SQLITE_RAG_ENABLED=true` or `RAG_BACKEND=sqlite`; hardware benchmarking and sqlite-vec search are still open.

Source: https://github.com/asg017/sqlite-vec

## 2. Signed Knowledge Packs

Implementation status: `backend/services/rag_service/knowledge_pack.py` now validates directory and zip packs with a v1 `manifest.json`, document checksums, expiration fields, and optional signature metadata.

EVY will eventually answer safety-relevant questions from local data. That means the system needs to know where data came from, when it expires, and whether it was tampered with.

Knowledge packs should be immutable bundles:

```text
knowledge-pack.zip
  manifest.json
  sources.json
  documents/
  checksums.json
  signature
```

Minimum manifest fields:

- `pack_id`
- `region`
- `created_at`
- `expires_at`
- `source_owner`
- `source_urls`
- `emergency_priority`
- `schema_version`
- `content_hash`

Possible signing approaches:

- Simple first version: minisign or age/SOPS-managed signing key.
- Robust later version: The Update Framework for threshold signatures, rollback protection, and secure update metadata.

What EVY would gain:

- Safer local RAG updates.
- Clear stale-data warnings.
- Ability to accept community/county/emergency-office data without blindly trusting files.
- Reproducible knowledge imports.

Decision: v1 schema and validation are implemented. Real signature verification and production signing policy remain required before real community or emergency-office data is trusted.

Source: https://theupdateframework.io/

## 3. Hardware Watchdog And Read-Only Root

Implementation status: `scripts/boot_self_check.py` now writes `boot_self_check_report.json` and makes simulation-vs-hardware visibility explicit. The actual Raspberry Pi watchdog, systemd watchdog, and read-only-root setup remain hardware-cycle work.

This is not glamorous, but it may be one of the highest-value field features.

EVY should assume:

- Power will drop.
- SD cards will be stressed.
- A service may hang.
- A node may be physically unreachable.

Recommended pattern:

- Enable Raspberry Pi hardware watchdog.
- Add systemd watchdog settings for core services.
- Use read-only root or overlay root for OS partitions.
- Keep explicit writable paths for:
  - `/data`
  - `/logs`
  - model cache
  - software reports
- Write a boot self-check report after every reboot.

What EVY would gain:

- Better recovery from hangs.
- Lower risk of filesystem corruption.
- Clear evidence after reboots.
- Safer solar/battery testing.

Decision: plan now, implement during first Pi bring-up.

## 4. OpenTelemetry Collector

Implementation status: stable metric names are defined in `backend/shared/observability.py`. A lightweight local Collector profile is available in `monitoring/otel-collector.yaml` with the overlay `docker-compose.observability.yml`; deeper service instrumentation is still open.

EVY needs observability that works offline first and can export later. OpenTelemetry Collector is vendor-neutral and can receive, process, and export telemetry. The official docs describe it as a collector for traces, metrics, and logs with multiple deployment patterns.

What EVY should collect:

- SMS receive-to-response latency.
- Queue depth and retry count.
- BitNet inference latency and failures.
- RAG search latency and hit count.
- GSM signal quality.
- Battery voltage/current/temperature when telemetry exists.
- Emergency message count.
- Reboot count.

Suggested first profile:

- Local collector in `docker-compose.observability.yml`.
- OTLP receiver.
- File or debug exporter.
- Later optional Prometheus exporter.

Decision: lightweight local profile is implemented. Keep it optional until the first GSM plus local BitNet node is stable.

Source: https://opentelemetry.io/docs/collector/

## 5. Meshtastic

EVY has custom LoRa and mesh design work. That is valuable, but mesh networking is a large problem. Meshtastic is an open-source, off-grid, decentralized mesh network built for low-power LoRa devices. Its docs emphasize no cell towers, no internet, peer-to-peer LoRa communication, and encrypted messaging.

How EVY could use it:

- Send node status beacons.
- Relay short emergency notices.
- Exchange "knowledge pack available" messages.
- Test multi-node field topology without building all mesh logic first.

Risks:

- Adds another firmware/device ecosystem.
- Payload constraints may not match EVY message types.
- Need to evaluate region/legal settings carefully.
- Should not distract from first GSM plus local LLM bring-up.

Decision: spike after single-node hardware is stable.

Source: https://meshtastic.org/

## 6. NATS JetStream

Redis queueing currently works, but EVY has already hit queue serialization and visibility issues. NATS JetStream could become the durable local event backbone if queue behavior keeps growing.

JetStream consumers can provide at-least-once delivery. The official docs describe stateful consumers that track delivery and acknowledgments, with redelivery when messages are not acknowledged.

Potential EVY streams:

- `SMS.INBOUND`
- `SMS.ROUTED`
- `LLM.REQUESTED`
- `LLM.RESPONDED`
- `SMS.OUTBOUND`
- `EMERGENCY.EVENT`
- `NODE.TELEMETRY`

What EVY would gain:

- Replayable event history.
- Clear durable acknowledgments.
- Better local audit trail.
- Cleaner future multi-process service boundaries.

Risks:

- Adds a new service.
- Redis is already present.
- Migration before hardware may distract from GSM/LLM validation.

Decision: do not block hardware. Spike only if queue complexity grows.

Source: https://docs.nats.io/nats-concepts/jetstream

## 7. OTA Updates With RAUC Or Mender

Once nodes are deployed, updates need rollback. Manual SSH is fine on the bench and fragile in the field.

Two viable directions:

- RAUC: robust embedded Linux update controller.
- Mender: broader OTA update platform for embedded Linux fleets.

What EVY would gain:

- Safer image updates.
- Rollback after failed update.
- Better fleet discipline.
- Less risk during remote deployments.

Decision: choose update strategy before field deployment, not before first bench hardware tests.

Sources:

- https://rauc.io/
- https://mender.io/

## 8. Plus Codes

Implementation status: `backend/services/sms_gateway/message_parser.py` now detects Plus Code tokens and preserves `location.plus_code`, `location.normalized`, and `location.source = "sms_plus_code"`.

Plus Codes, also called Open Location Code, are compact text location references. They are useful when street addresses are missing, ambiguous, or too long for SMS.

EVY examples:

```text
HELP 86HVCWC8+R9
SHELTER NEAR 86HVCWC8+R9
STATUS 86HVCWC8+R9
```

What EVY would gain:

- Offline-compatible location references.
- SMS-friendly emergency location format.
- Easier matching between user message and local resource directory.

Decision: parser support is implemented and covered by SMS gateway tests.

Source: https://github.com/google/open-location-code

## 9. Syncthing

Syncthing can synchronize files between devices without a central cloud server. For EVY, it should be limited to immutable artifacts, not live databases.

Good uses:

- Software reports.
- Signed knowledge packs.
- Benchmark artifacts.
- Operator notes.

Avoid:

- Active SQLite databases.
- Chroma/vector database directories.
- Secret files.

Decision: later convenience feature, not core runtime.

Source: https://docs.syncthing.net/

## 10. whisper.cpp

EVY is SMS-first, so speech should not distract from the core node. But local speech-to-text could be valuable for an operator/base-station console.

Potential uses:

- Operator speaks incident notes.
- Local transcript becomes an SMS-ready alert.
- Post-event interviews become structured notes.

Decision: optional bigEVY/operator feature, not lilEVY hardware blocker.

Source: https://github.com/ggml-org/whisper.cpp

## Suggested Phasing

### Before Hardware Arrives

- Add signed knowledge-pack schema. Done for v1 manifest validation.
- Prototype SQLite RAG store behind a feature flag. Done for FTS5 search and pack import.
- Add Plus Code parsing tests if time permits. Done.
- Add local observability metrics names even before OpenTelemetry is deployed. Done.

### First Hardware Cycle

- Hardware watchdog and boot self-check.
- Measure BitNet performance and power.
- Validate read-only root or overlay-root approach.
- Keep Meshtastic out until GSM plus local LLM is stable.

### After Single-Node Stability

- Meshtastic spike.
- Expand OpenTelemetry instrumentation and dashboards.
- NATS JetStream queue/event spike.
- OTA update architecture decision.

### Later

- Syncthing for immutable artifact movement.
- whisper.cpp for operator console workflows.

## What Not To Add Yet

- Kubernetes: too heavy for a first lilEVY node.
- Full service mesh: not useful on one Pi.
- Cloud-only observability: conflicts with offline-first field behavior.
- Blockchain-style identity or storage: unnecessary complexity.
- More LLM backends before BitNet is measured: would dilute the current local inference work.
