# EVY Observability

EVY now has stable metric names and an optional local OpenTelemetry Collector profile.

Status: local profile scaffold is implemented. It is not required for the first hardware bring-up, and services still need deeper instrumentation before this becomes a full dashboard.

## Metric Names

Stable names live in:

- `backend/shared/observability.py`

Initial names cover:

- SMS receive-to-response latency
- SMS queue depth and retry count
- BitNet inference latency and failures
- RAG search latency, hits, and misses
- emergency message count
- battery voltage/current/temperature
- node reboot count

## Local Collector

Collector config:

- `monitoring/otel-collector.yaml`

Compose overlay:

- `docker-compose.observability.yml`

Start the collector by itself:

```bash
docker compose -f docker-compose.observability.yml up
```

Start it with the main stack:

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up
```

Local ports:

- OTLP gRPC: `4317`
- OTLP HTTP: `4318`
- Prometheus exporter: `9464`

Local file output:

- `logs/otel/evy-otel.json`

The profile exports locally first using debug, file, and Prometheus exporters. Cloud/export destinations should wait until the first node is stable and privacy rules are clear.

## Validation

```bash
python -m pytest backend/tests/test_observability_and_boot.py backend/tests/test_observability_profile.py -q
docker compose -f docker-compose.observability.yml config --quiet
```

## Remaining Work

- Add real counters/timers around SMS, BitNet, RAG, queue, and power paths.
- Add a small Grafana dashboard or local text report.
- Decide whether the collector runs on the Pi during early bench tests or only during diagnostics.
- Add export rules after privacy and field-data handling are decided.
