# EVY — Repository Gap Analysis & Strategic Roadmap
### Incorporating 1-bit Inferencing, Edge Deployment, and Next-Phase Architecture
*Prepared by Claude | March 2026*

---

## 1. Executive Summary

EVY is a well-conceived project with a clear mission: democratize AI access via SMS over off-grid mesh infrastructure. After a full read of every service, configuration, and documentation file in the repository, the picture is one of strong conceptual design and significant documentation investment, sitting on top of a backend that is roughly 50–60% implemented. The architecture is sound. The gaps are real and fixable. The arrival of 1-bit inferencing (BitNet b1.58 2B4T) changes the calculus of what lilEVY can do autonomously, and should drive a meaningful pivot in Phase 3.

> **Overall verdict:** Repo is documentation-heavy, code-light. Much of what is described in the Phase 10–14 docs does not yet exist as running code. The core SMS → Router → LLM → RAG pipeline is wired but depends on Ollama/OpenAI connectivity that defeats the off-grid premise until replaced.

---

## 2. Infrastructure Review

### 2.1 Container Architecture

The Docker Compose setup is well-structured. lilEVY gets its own compose file with 6 services on an isolated bridge network (172.20.0.0/16). Services are correctly separated: `sms-gateway`, `message-router`, `tiny-llm`, `local-rag`, `privacy-filter`, `node-communication`, and `monitoring`. The port allocation is clean (8000–8005 + 9090).

**Key gaps:**

- **ARM build broken.** `Dockerfile.lilevy` is based on `python:3.9-slim` and installs the full `requirements.txt` including `torch==2.1.2` and `transformers==4.36.2`. On a Pi 4 ARM64, PyTorch 2.1.2 via pip installs an x86 wheel that will not run. This will silently fail at runtime.

- **No model volume on first boot.** `docker-compose.lilevy.yml` mounts `./models/tiny:/models` for the `tiny-llm` service but takes no step to populate that directory. On first boot, no model will be present and the fallback response path activates immediately.

- **Offline-first config is missing.** `config.py` sets `default_model = "gpt-4"` and `llm_provider = "openai"`. On a Pi with no internet, every non-template query fails. There is no offline-first default anywhere in the config.

- **Broad /dev mount.** `docker-compose.lilevy.yml` maps `/dev:/dev:rw` for GSM access. A targeted `--device` flag is already present for `ttyUSB0` specifically; the broad mount is redundant and a security concern.

- **No health check chaining.** If `local-rag` fails to start (e.g., ChromaDB init fails due to missing persist dir), `message-router` starts anyway and will silently return error responses.

### 2.2 Deployment Scripts

- No Pi-specific build target. Scripts run `docker-compose build` with no cross-compilation or ARM-specific step.
- `deploy-lilevy.sh` sets `DEFAULT_MODEL=tinyllama` but takes no action to pull or validate a model before starting services.
- No rollback mechanism. If a deployment fails partway through, persistent volumes may contain corrupt state.

### 2.3 Monitoring

Prometheus config exists and the port is exposed. `prometheus-fastapi-instrumentator` is in requirements. However: no dashboards are defined, no alerting rules exist, and Grafana (referenced in `config.py` at port 3001) has no compose service defined.

| Component | Status | Notes |
|---|---|---|
| Container networking | ✅ Complete | Isolated bridge networks, correct port allocation |
| ARM/Pi build target | ❌ Missing | requirements.txt will fail PyTorch install on ARM64 |
| Offline-first defaults | ❌ Missing | config.py defaults to gpt-4/openai — fatal off-grid |
| Model pre-loading on boot | ❌ Missing | No pull/validate step in deploy scripts |
| Health check chaining | ❌ Missing | Services start without dependency readiness checks |
| Prometheus config | 🟡 Partial | Config exists, no dashboards or alerts defined |
| Grafana | ❌ Missing | Referenced in config but no compose service |
| Rollback mechanism | ❌ Missing | No failure cleanup in deploy scripts |
| GSM device access | 🟡 Partial | ttyUSB0 mapped but also broad /dev:rw mount |

---

## 3. Database Review

### 3.1 ChromaDB (Vector Store)

ChromaDB is correctly chosen for edge RAG. The implementation in `rag_service/main.py` initializes a `PersistentClient` with a configurable path. Documents are added with metadata. The embedding service uses `all-MiniLM-L6-v2` via sentence-transformers with a local cache.

**Critical issues:**

- ChromaDB pinned at `0.4.22`. Current stable is `0.6.x` with significant API changes. No migration path defined.

- `document_manager.py` stores documents as raw JSON at `/data/evy_knowledge/documents.json`. ChromaDB and DocumentManager are two separate stores that are manually synced in `_sync_local_documents()`. The sync logic compares **document counts, not IDs** — deletions in one store will never be caught.

- The embedding cache lives at `/tmp/evy_models/embedding_cache.json`. On Pi, `/tmp` is RAM-backed tmpfs. Reboots wipe the cache entirely.

- `search_documents()` in `document_manager.py` does purely lexical search (string contains, keyword overlap). It does **not** use vector embeddings. ChromaDB and DocumentManager are operating independently — DocumentManager is a dead code path for actual retrieval.

- `RAGQuery` has a `filter_metadata` field but it is not passed through to `collection.query()` calls.

### 3.2 PostgreSQL

`requirements.txt` includes `psycopg2-binary` and SQLAlchemy 2.0. `docker-compose.lilevy.yml` does not include a Postgres service. `config.py` has a `database_url` pointing to a postgres container that does not exist in the lilEVY compose. This will cause import failures at startup for any code that attempts a DB connection.

> **Note:** The Postgres dependency is vestigial from early development. For lilEVY, SQLite or full removal is correct. Running Postgres on a Pi 4 for this use case is wasteful and brittle.

### 3.3 Redis / Celery

The message queue in `sms_gateway/message_queue.py` uses an in-memory queue — not Redis. Redis and Celery are in `requirements.txt` but no Redis service exists in `docker-compose.lilevy.yml`. The in-memory queue works, but the redis import at startup may cause failures.

| Component | Status | Notes |
|---|---|---|
| ChromaDB vector store | 🟡 Partial | Works but version is old, no metadata filter in query path |
| DocumentManager JSON store | 🟡 Partial | Count-based sync with ChromaDB, not ID-based — drift-prone |
| Embedding cache persistence | ❌ Missing | Cache in /tmp — wiped on every reboot |
| Vector search (actual) | 🟡 Partial | ChromaDB query works; DocumentManager search is lexical only |
| PostgreSQL | ❌ Missing | In requirements/config but no compose service for lilEVY |
| Redis | ❌ Missing | In requirements but not in compose; in-memory queue used instead |
| Database migrations | ❌ Missing | No Alembic migrations defined despite alembic in requirements |

---

## 4. RAG Pipeline Review

### 4.1 Pipeline Architecture

The intended RAG flow is: SMS in → MessageParser (intent/category) → MessageRouter → RAGQuery to `local-rag` → embed with `all-MiniLM-L6-v2` → ChromaDB similarity search → top-k docs → prepend to LLM prompt → response. This is a correct and reasonable design.

### 4.2 Embedding Service

`LocalEmbeddingService` uses `all-MiniLM-L6-v2`, a 22M parameter model producing 384-dim embeddings. Good choice for Pi: fast, small, usable. `encode_text()` correctly wraps the synchronous `SentenceTransformer.encode()` in `loop.run_in_executor()` to avoid blocking the FastAPI event loop.

- Model cache directory should be a persistent volume mount, not `/tmp`.
- `SimpleEmbeddingService` (TF-IDF fallback) is correctly coded but the quality drop-off is significant.

### 4.3 Knowledge Base Quality

The `scripts/` directory contains 30+ Python scripts for building the knowledge base. These generate synthetic/curated knowledge entries and write them to JSON. The README claims 626 entries at 15.4MB.

- None of these scripts have been run against the actual repository. The `/data` directory is not committed (correctly). A first-time deployer has no automated way to know they need to run all 30 scripts. **There is no single bootstrap command.**
- The knowledge is Wichita-specific in places (`env.wichita`, `build_wichita_knowledge.py`). For a global humanitarian use case this needs to be parameterized by deployment region.
- Knowledge entries are generated **synthetically**. For emergency procedures specifically, synthetic content is a liability. CPR, first aid, and emergency protocol content must come from verified sources (Red Cross, FEMA, WHO).
- No versioning or checksumming of knowledge entries. The `BIGEVY_LILEVY_SYNC_SYSTEM.md` describes checksum-based sync; it is not implemented in the actual sync code.

### 4.4 Query Path Gaps

> **Gap:** The 160-char hard truncation in `TinyLLMService.generate_response()` happens **after** generation, not before. The model generates a full response then it is sliced. This wastes inference time and produces jarring mid-sentence cutoffs. The prompt should instruct the model to generate a complete SMS-length answer; truncation should be a safety net only.

> **Gap:** There is no RAG result quality threshold. If ChromaDB returns 3 documents with cosine similarity of 0.1 (essentially noise), they are still prepended to the LLM prompt as authoritative context. A minimum similarity score threshold (e.g., 0.6) should gate whether RAG results are used at all.

> **Critical gap:** The intent classifier in `message_parser.py` is regex-based keyword matching. There is no ML classification. For the emergency detection path specifically, this is brittle — `"my car is on fire"` will not match the emergency keyword list as written.

| Component | Status | Notes |
|---|---|---|
| Embedding model (all-MiniLM-L6-v2) | 🟡 Partial | Good model choice, cache is in /tmp — not persistent |
| ChromaDB query path | 🟡 Partial | Works, but no similarity threshold filtering |
| Knowledge base content | ❌ Missing | 626-entry KB requires 30+ scripts run manually |
| Emergency keyword detection | 🟡 Partial | Regex-based, brittle for natural language |
| RAG → LLM context injection | ✅ Complete | Correctly wired |
| Response length management | 🟡 Partial | Hard 160-char truncate post-generation |
| Knowledge versioning/sync | ❌ Missing | Described in docs, not implemented in code |
| Region parameterization | ❌ Missing | Wichita-specific defaults |
| Authoritative source verification | ❌ Missing | Emergency content is synthetically generated |

---

## 5. 1-Bit Inferencing: Impact Assessment

### 5.1 What Changes for lilEVY

BitNet b1.58 2B4T runs at 5.57–6.43 tokens/second on a Raspberry Pi 5 and 11 tokens/second with T-MAC optimization. The model fits in under 500MB. This rewrites the constraints EVY was designed around.

| Constraint | Before BitNet | After BitNet |
|---|---|---|
| Local model size | 125M TinyLlama (~700MB) | 2B BitNet b1.58 (~500MB) |
| Reasoning quality | Very limited, hallucination-prone | Comparable to GPT-3.5 for short tasks |
| Inference speed on Pi 4 | 3–5 tokens/sec | 5–8 tokens/sec (estimated) |
| Power draw during inference | ~5.5W | ~3–4W (55–70% reduction) |
| Off-grid query capability | Simple lookups only | Multi-step reasoning, triage, procedures |
| bigEVY dependency | Required for complex queries | Optional — most queries local |
| GPU requirement (bigEVY) | Required for 7B+ models | 100B BitNet on single CPU |
| LoRa bandwidth usage | High — many offloads to bigEVY | Low — most resolved locally |

### 5.2 Architectural Implications

- **`_is_model_suitable_for_lilevy()` must be updated.** Currently blocks any model not in a hardcoded list of 125M–350M parameter models. BitNet 2B must be added and the size ceiling raised. 3-line code change with large downstream impact.

- **A new model backend is required.** The current loading path uses Ollama as primary, falling back to Hugging Face transformers. BitNet requires `bitnet.cpp` (Microsoft's inference framework built on llama.cpp) — neither Ollama nor transformers serves it natively. A `BitNetModelManager` class parallel to `TinyModelManager` is the right pattern.

- **Multi-SMS chunked responses become viable.** With BitNet 2B quality, a response strategy of delivering chunked answers (`Step 1 of 3: ...`) across sequential SMS messages is worth implementing for complex queries.

- **Smart router thresholds need rethinking.** `QueryComplexity.COMPLEX` currently pushes queries to `INTERNET` or `LORA` layers. With BitNet 2B locally, most queries classified as COMPLEX today should resolve locally.

---

## 6. Edge Use Cases

### 6.1 What Works Today (with P0 fixes applied)

- Emergency keyword detection → static response dispatch (call 911, CPR steps, tornado shelter). Works without LLM once keyword matching is fixed.
- Local services directory lookup ("nearest hospital", "food bank hours"). Pure RAG retrieval — no LLM needed if knowledge base is populated.
- Weather alert relay. If the sync service fetches NWS API data at build time, this is a pure retrieval query.
- Simple FAQ-style queries against the knowledge base.

### 6.2 Use Cases Unlocked by BitNet 2B

- **Medical triage over SMS.** "My child has a fever of 104 and a rash — what do I do?" requires multi-step reasoning. TinyLlama will hallucinate. BitNet 2B can produce clinically appropriate guidance with disclaimers baked into the system prompt.
- **Agricultural advisory.** "My tomatoes have yellowing leaves and brown spots" — pattern-matching + reasoning where BitNet 2B + a local agricultural knowledge base produces genuinely useful output.
- **Legal rights in plain language.** "Can my landlord enter without notice?" — jurisdiction-specific RAG context + BitNet 2B reasoning produces accurate, concise answers.
- **Disaster response coordination.** Multi-step instruction sequences require a model that can follow conditional logic and produce structured output. TinyLlama cannot reliably do this.
- **Mental health triage.** Safe messaging guidelines for crisis situations require careful reasoning about context. BitNet 2B's quality level makes this viable where TinyLlama is not.
- **Multilingual queries.** BitNet b1.58 is being developed with multilingual capability — transformative for non-English deployments.

### 6.3 Use Cases That Remain bigEVY-Dependent

- Long-form document generation or summarization (context window limitations).
- Real-time data queries (weather NOW, current road conditions) — need live API access.
- Complex multi-turn reasoning where context accumulates over many SMS exchanges.
- Model updates and knowledge base refreshes — should flow bigEVY → lilEVY nodes.

---

## 7. Strategic Alignment & Prioritized Next Steps

### 7.1 Revised Architecture Thesis

The original EVY design positioned lilEVY as a thin edge node that offloads complexity to bigEVY. BitNet inverts this. The revised thesis:

> **lilEVY is the primary compute node. bigEVY is the sync and refresh node. LoRa is for node-to-node coordination, not query offloading.**

> **Principle:** Redesign the smart router around a "local first, always" policy. A query only leaves the node if: (a) it requires real-time external data, (b) it exceeds the context window of the local model, or (c) no local knowledge exists AND a bigEVY node is reachable within the LoRa timeout.

### 7.2 Prioritized Initiative Stack

| Priority | Initiative | Effort | Impact |
|---|---|---|---|
| **P0** | Fix offline-first config: change `config.py` defaults to `ollama`/local model; add `BITNET_MODEL` env var and model-pull step in deploy scripts | 1 day | Unlocks off-grid operation |
| **P0** | Fix PyTorch ARM build: add aarch64-specific install path in `Dockerfile.lilevy` using prebuilt wheels | 1 day | Required for any inference on Pi |
| **P0** | Move embedding cache from `/tmp` to a persistent volume mount | 2 hours | Prevents full re-embedding on every reboot |
| **P0** | Add similarity score threshold to RAG query path (min 0.5 cosine) | 2 hours | Eliminates low-quality context injection |
| **P1** | Build BitNet model backend: add `bitnet.cpp` as inference option; create `BitNetModelManager` parallel to `TinyModelManager` | 3–5 days | Unlocks 2B quality on Pi 4/5 |
| **P1** | Raise `_is_model_suitable_for_lilevy()` ceiling; add `bitnet-2b` to suitable models list | 2 hours | Required for BitNet to load |
| **P1** | Replace count-based sync with ID-based sync between `DocumentManager` and ChromaDB | 1 day | Prevents knowledge base drift |
| **P1** | Create single bootstrap script: run all 30 `build_*.py` scripts in dependency order, validate output, import to ChromaDB | 2 days | First-time deployer experience |
| **P1** | Implement similarity threshold + multi-SMS chunked response for complex queries | 2 days | Enables medical/legal triage use case |
| **P2** | Upgrade ChromaDB to 0.6.x with migration script | 1–2 days | Security patches, API improvements |
| **P2** | Remove PostgreSQL and Celery/Redis from `requirements.txt` for lilEVY; use SQLite for any structured storage | 1 day | Eliminates phantom dependencies, reduces image size |
| **P2** | Add NWS (National Weather Service) free API integration to knowledge sync | 2 days | High-value, off-grid-appropriate data source |
| **P2** | Parameterize knowledge base by deployment region (lat/lon bounding box + region config in `env.template`) | 3 days | Transforms from Wichita demo to deployable product |
| **P2** | Replace Prometheus-only monitoring with a lightweight on-device status command (`!status` via SMS) backed by SQLite metrics | 3 days | Operations without a laptop on the node |
| **P3** | Redesign smart router around local-first policy with BitNet quality thresholds | 2–3 days | Architecture alignment with new model capability |
| **P3** | Redesign bigEVY as knowledge sync + model update server only (strip LLM inference requirement) | 1 week | Dramatically lowers bigEVY hardware cost |
| **P3** | Add multilingual query detection and routing for non-English deployments | 1 week | Expands mission scope globally |
| **P3** | Integrate authoritative emergency content: Red Cross, FEMA, WHO via structured import | 2 weeks | Liability reduction + quality uplift for life-safety queries |

---

## 8. LoRa Mesh: Current State & Gaps

`lora_radio_service.py` is well-structured with proper message types (`DISCOVERY`, `ROUTE`, `DATA`, `SYNC`, `EMERGENCY`, `HEARTBEAT`, `ACK`), a `LoRaMessage` dataclass, and `NodeInfo` tracking. The routing table and `known_nodes` state are correctly maintained in memory.

**Gaps:**

- `hardware_simulated = True` on initialization. The actual SX1276 hardware interface is not implemented. The service runs in simulation mode with no physical radio communication. `EVY_MESH_NETWORKING_PROTOCOLS.md` describes the protocol in detail but the hardware binding layer does not exist.
- LoRa HAT integration requires `spidev` and `RPi.GPIO` — neither is in `requirements.txt`.
- Message encryption (AES-256, digital signatures) is described in docs but not implemented in `LoRaMessage` or the radio service.
- `EVY_LOW_FREQUENCY_RADIO_INTEGRATION.md` describes APRS and HF radio as future extensions (100+ mile range for truly remote deployments) — correctly deferred but worth keeping on the P3 radar.

| Component | Status | Notes |
|---|---|---|
| LoRa protocol definition | ✅ Complete | MessageTypes, routing, NodeInfo all well-defined |
| LoRa hardware binding (SX1276) | ❌ Missing | `hardware_simulated=True`, no actual radio code |
| Mesh routing algorithm | 🟡 Partial | Routing table logic present, hardware not callable |
| AES-256 message encryption | ❌ Missing | Described in docs, not in code |
| spidev/RPi.GPIO dependencies | ❌ Missing | Not in requirements.txt |
| APRS/HF radio extension | 📋 Planned | Documented, correctly deferred to Phase 4+ |

---

## 9. Testing Coverage Assessment

Tests exist in `backend/tests/` for SMS gateway, LLM inference, and integration. The test structure is correct (pytest + asyncio + mock).

- `test_sms_gateway.py` covers initialization, rate limiting, emergency priority detection, and message forwarding. Good coverage of the happy paths.
- No tests exist for the RAG pipeline end-to-end. ChromaDB query paths, embedding service, and document manager have zero test coverage.
- No tests for the LoRa radio service in simulation mode.
- No tests for `smart_router.py` layer selection logic.
- No load testing or concurrency testing. A Pi 4 handling 10 simultaneous SMS queries while running BitNet inference will behave differently than sequential testing suggests.

---

## 10. Summary Scorecard

| Component | Status | Notes |
|---|---|---|
| SMS Gateway (GSM driver, queue, parser) | 🟡 Partial | Code exists, hardware simulation mode only |
| Message Router (classification, dispatch) | 🟡 Partial | Works for basic cases; regex intent detection brittle |
| Tiny LLM Service | 🟡 Partial | Ollama/transformers backend; ARM build broken; BitNet not supported |
| RAG Service (ChromaDB) | 🟡 Partial | Pipeline correct; no similarity threshold; cache not persistent |
| Knowledge Base (626 entries) | ❌ Missing | Requires manual run of 30 build scripts; not bootstrapped |
| LoRa Mesh Service | 🟡 Partial | Protocol designed; hardware binding missing |
| Smart Router | 🟡 Partial | Layer scoring logic present; no BitNet-aware thresholds |
| bigEVY Core Services | 🟡 Partial | Large LLM + Global RAG implemented; 4 of 8 services missing |
| Deployment Scripts | 🟡 Partial | Docker compose works; ARM build target missing; no model pull |
| Monitoring (Prometheus) | 🟡 Partial | Config exists; no dashboards, no Grafana service |
| Testing | 🟡 Partial | SMS gateway covered; RAG, LoRa, router have no tests |
| 1-Bit Inferencing (BitNet) | ❌ Missing | Not yet integrated; code changes identified and scoped |
| Knowledge Region Parameterization | ❌ Missing | Wichita-specific; needs deployment-region abstraction |
| Authoritative Emergency Content | ❌ Missing | Synthetically generated; needs verified sources |

---

**Bottom line:** EVY has strong bones. The microservice architecture is sound, the data models are well-designed, and the mission is coherent. The work to make it actually run off-grid on Pi hardware is a P0/P1 sprint of roughly 2–3 weeks. The BitNet integration that transforms its capability is another 1–2 weeks on top of that. This is not a rebuild — it is a focused hardening sprint followed by a well-defined capability upgrade.

---
*EVY Gap Analysis | srex-dev | March 2026*
