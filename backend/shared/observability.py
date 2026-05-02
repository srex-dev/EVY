"""Stable observability names for EVY local-first telemetry."""


class MetricNames:
    SMS_RECEIVE_TO_RESPONSE_LATENCY_MS = "evy.sms.receive_to_response_latency_ms"
    SMS_QUEUE_DEPTH = "evy.sms.queue_depth"
    SMS_RETRY_COUNT = "evy.sms.retry_count"
    BITNET_INFERENCE_LATENCY_MS = "evy.bitnet.inference_latency_ms"
    BITNET_INFERENCE_FAILURES = "evy.bitnet.inference_failures"
    RAG_SEARCH_LATENCY_MS = "evy.rag.search_latency_ms"
    RAG_HIT_COUNT = "evy.rag.hit_count"
    RAG_MISS_COUNT = "evy.rag.miss_count"
    EMERGENCY_MESSAGE_COUNT = "evy.emergency.message_count"
    POWER_BATTERY_VOLTAGE = "evy.power.battery_voltage"
    POWER_BATTERY_CURRENT = "evy.power.battery_current"
    POWER_TEMPERATURE_C = "evy.power.temperature_c"
    NODE_REBOOT_COUNT = "evy.node.reboot_count"


ALL_METRIC_NAMES = [
    value
    for key, value in MetricNames.__dict__.items()
    if key.isupper() and isinstance(value, str)
]
