# EVY Software Validation Checklist

Use this checklist before hardware edge validation and release tagging.

## Validation Stages

1. Pre-merge quality checks
2. Core regression tests
3. Integration tests
4. Performance/load checks
5. Fault-injection and offline checks
6. Release gate evidence

## 1) Pre-Merge Quality Checks

- [ ] Lint checks pass for changed modules
- [ ] No new linter errors in touched files
- [ ] Basic import/runtime sanity checks pass
- [ ] Config defaults are valid for offline-first mode

Recommended:

```bash
python scripts/test_software_suite.py --stage premerge
```

## 2) Core Regression Tests

- [ ] `backend/tests/test_llm_inference.py` passes
- [ ] `backend/tests/test_llm_rag_tuning_script.py` passes
- [ ] `backend/tests/test_knowledge_pack.py` passes
- [ ] `backend/tests/test_knowledge_pack_script.py` passes
- [ ] `backend/tests/test_hardware_suite_report.py` passes
- [ ] `backend/tests/test_sqlite_rag_store.py` passes
- [ ] `backend/tests/test_observability_and_boot.py` passes
- [ ] `backend/tests/test_observability_profile.py` passes
- [ ] `backend/tests/test_pi_bootstrap_check.py` passes
- [ ] `backend/tests/test_message_router_enhancements.py` passes
- [ ] `backend/tests/test_routing_and_models.py` passes
- [ ] `backend/tests/test_sms_gateway.py` passes

Recommended:

```bash
python scripts/test_software_suite.py --stage regression
```

## 3) Integration Tests

- [ ] Service-to-service flow passes (SMS -> Router -> LLM/RAG -> SMS)
- [ ] Health endpoints respond for all required services
- [ ] Redis fallback behavior works (direct-send mode)
- [ ] RAG threshold behavior returns only high-confidence context

Recommended:

```bash
python scripts/test_software_suite.py --stage integration
```

## 4) Performance and Load Checks

- [ ] Concurrent API requests remain stable
- [ ] Queue depth does not grow unbounded at target load
- [ ] p95 and p99 latency are within target SLOs
- [ ] Emergency paths stay responsive under normal load

Recommended:

```bash
python scripts/test_software_suite.py --stage performance
```

## 5) Fault-Injection and Offline Checks

- [ ] Behavior validated with internet unavailable
- [ ] Behavior validated with Redis unavailable
- [ ] Behavior validated with service restarts during traffic
- [ ] No crash loops after transient dependency failures

Recommended:

```bash
python scripts/test_software_suite.py --stage resilience
```

## 6) Release Gate Evidence

- [ ] Software suite report JSON generated and archived
- [ ] Failures (if any) are triaged and resolved
- [ ] Release candidate commit/tag references report artifact
- [ ] `release_gates.pass` is `true` in software suite report
- [ ] Performance subset gate elapsed <= 30 seconds
- [ ] Retry-path gate passes (`message_queue_retries`)
- [ ] Deterministic pre-hardware smoke test passes
- [ ] Full backend pytest suite passes
- [ ] Rust crates pass `cargo test`
- [ ] Frontend installs and builds
- [ ] Main Compose config parses cleanly
- [ ] Core lilEVY Compose config parses cleanly
- [ ] Lightweight pre-hardware Compose smoke passes when Docker is available
- [ ] BitNet manager tests pass
- [ ] If BitNet runtime/model are installed, LLM health reports `details.bitnet.available = true`
- [ ] If BitNet runtime/model are installed, `python scripts/validate_bitnet_local_llm.py --run-inference` passes and report is archived
- [ ] If BitNet service is running, `python scripts/benchmark_bitnet_sms_prompts.py` passes and report is archived
- [ ] LLM/RAG tuning report records retrieval pass/fail and LLM availability
- [ ] Knowledge-pack validation tests pass
- [ ] Sample knowledge-pack CLI import/search report passes
- [ ] SQLite RAG import/search tests pass
- [ ] Plus Code parser metadata test passes
- [ ] Boot self-check report scaffold test passes
- [ ] Hardware validation report artifact shape test passes
- [ ] OpenTelemetry Collector profile test passes
- [ ] Raspberry Pi bootstrap check report shape test passes

Recommended full run:

```bash
python scripts/test_software_suite.py --stage full
python scripts/pre_hardware_smoke.py
python scripts/pre_hardware_compose_smoke.py --base-port 18100
python -m pytest backend/tests -q
python -m pytest backend/tests/test_bitnet_cpp_manager.py backend/tests/test_bitnet_validation_script.py backend/tests/test_bitnet_sms_benchmark.py backend/tests/test_llm_inference.py -q
python -m pytest backend/tests/test_hardware_suite_report.py backend/tests/test_knowledge_pack.py backend/tests/test_knowledge_pack_script.py backend/tests/test_llm_rag_tuning_script.py backend/tests/test_sqlite_rag_store.py backend/tests/test_observability_and_boot.py backend/tests/test_observability_profile.py backend/tests/test_pi_bootstrap_check.py backend/tests/test_sms_gateway.py -q
python scripts/validate_knowledge_pack.py --require-signature --import-sqlite --search "boil water"
python scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1
python scripts/pi_bootstrap_check.py
python scripts/boot_self_check.py
cd backend/rust_services/sms_gateway && cargo test
cd ../message_router && cargo test
cd ../compression && cargo test
cd ../../../frontend && npm install && npm run build
cd .. && docker compose config --quiet
docker compose -f docker-compose.lilevy.yml config --quiet
docker compose -f docker-compose.prehardware.yml config --quiet
docker compose -f docker-compose.observability.yml config --quiet
```

## Suggested SLO Targets

- Route-only processing p95 < 500ms (excluding model inference)
- End-to-end normal query p95 < 45s
- Emergency path p95 < 15s under mixed load
- 0 message loss in restart/retry paths in test conditions
- Inbound queue depth <= 500 at target traffic
- LLM request timeout <= 20s with overload response instead of silent drop

## Report Artifact

Default output:

- `data/lilevy/software_reports/software_suite_report.json`
