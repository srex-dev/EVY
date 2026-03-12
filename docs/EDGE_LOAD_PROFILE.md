# EVY Edge Load Profile

This document defines the initial edge capacity envelope used by service backpressure and release gating.

## Target Envelope (lilEVY)

- Inbound SMS target: `20` messages/minute
- End-to-end p95 target: `<= 12s` (`12000ms`)
- Max queue depth target: `<= 500` pending messages
- Process memory ceiling: `<= 4096MB` per edge service

These targets are exposed in runtime health details and configured in `backend/shared/config.py`.

## Enforced Runtime Limits

- Inbound SMS queue max size: `500`
- Outbound queue max size: `1000`
- Router forward retries: `3` attempts
- Router forward timeout: `15s`
- LLM request timeout: `20s`
- Max in-flight LLM requests: `2`
- Max loaded LLM models: `2`

## Why This Envelope

- SMS is the control plane and must stay responsive under contention.
- LLM latency is variable on edge hardware and is bounded to avoid starving routing.
- Queue caps prevent unbounded memory growth under modem/network faults.
- Memory ceilings reserve headroom for OS, modem drivers, and telemetry tasks.

## Tuning Guidance

- If queue saturation occurs first, raise modem throughput or add downstream shedding before increasing queue depth.
- If p95 breaches before queue growth, reduce `llm_max_inflight_requests` or lower model complexity.
- If memory exceeds ceiling, reduce loaded model count and tighten RAG context/chunk parameters.
