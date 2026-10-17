from drivesense.analytics.hmi import hmi_metrics
from drivesense.models import TelemetryEvent


def event(**overrides: object) -> TelemetryEvent:
    defaults: dict[str, object] = {
        "event_id": "one",
        "vehicle_id": "v1",
        "trip_id": "t1",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "latitude": 0.0,
        "longitude": 0.0,
        "speed_kph": 0.0,
        "battery_soc": 50.0,
        "network_type": "LTE",
        "signal_dbm": -80.0,
        "latency_ms": 10.0,
        "connection_state": "CONNECTED",
        "object_detected": True,
    }
    defaults.update(overrides)
    return TelemetryEvent(**defaults)  # type: ignore[arg-type]


def test_hmi_metrics_detect_missing_false_and_latency_violations() -> None:
    missing = event(event_id="missing")
    slow = event(
        event_id="slow",
        warning_generated_at="2026-01-01T00:00:00.100+00:00",
        warning_displayed_at="2026-01-01T00:00:00.700+00:00",
    )
    false = event(
        event_id="false",
        object_detected=False,
        warning_displayed_at="2026-01-01T00:00:00.100+00:00",
    )
    result = hmi_metrics([missing, slow, false], latency_threshold_ms=500)
    assert (result.missing_warnings, result.false_warnings, result.threshold_violations) == (
        1,
        1,
        1,
    )
    assert result.missing_warning_rate == 0.5
    assert result.end_to_end_latency_p95_ms == 700.0
