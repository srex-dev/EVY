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

Recommended full run:

```bash
python scripts/test_software_suite.py --stage full
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
