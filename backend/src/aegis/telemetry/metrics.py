"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Info

# Application info
app_info = Info("aegis", "AegisProxy application information")

# Request metrics
requests_total = Counter(
    "aegis_requests_total",
    "Total number of requests processed",
    ["status", "endpoint"],
)

# Security metrics
pii_detections_total = Counter(
    "aegis_pii_detections_total",
    "Total number of PII entities detected",
    ["entity_type"],
)

injection_detections_total = Counter(
    "aegis_injection_detections_total",
    "Total number of injection attempts detected",
    ["pattern_type", "action"],
)

# Latency metrics
request_duration_seconds = Histogram(
    "aegis_request_duration_seconds",
    "Request duration in seconds",
    ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

filter_duration_seconds = Histogram(
    "aegis_filter_duration_seconds",
    "Filter processing duration in seconds",
    ["filter_name"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
)


def init_metrics(version: str) -> None:
    """Initialize application metrics."""
    app_info.info({
        "version": version,
        "name": "aegis-proxy",
    })
