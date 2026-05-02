"""Tests for the local OpenTelemetry Collector profile."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_otel_collector_profile_has_local_exporters():
    config = (ROOT / "monitoring" / "otel-collector.yaml").read_text(encoding="utf-8")

    assert "otlp:" in config
    assert "hostmetrics:" in config
    assert "prometheus:" in config
    assert "debug:" in config
    assert "file:" in config
    assert "/logs/otel/evy-otel.json" in config


def test_observability_compose_mounts_collector_config():
    compose = (ROOT / "docker-compose.observability.yml").read_text(encoding="utf-8")

    assert "otel/opentelemetry-collector-contrib" in compose
    assert "./monitoring/otel-collector.yaml:/etc/otelcol-contrib/config.yaml:ro" in compose
    assert "${EVY_OTEL_PROM_PORT:-9464}:9464" in compose
