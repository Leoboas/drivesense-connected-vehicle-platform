from drivesense.models import TelemetryEvent
from drivesense.quality.rules import quality_score, validate_event


def event(**overrides: object) -> TelemetryEvent:
    values: dict[str, object] = dict(
        event_id="one",
        vehicle_id="v1",
        trip_id="t1",
        timestamp="2026-01-01T00:00:00+00:00",
        latitude=0.0,
        longitude=0.0,
        speed_kph=20.0,
        battery_soc=50.0,
        network_type="LTE",
        signal_dbm=-80.0,
        latency_ms=20.0,
        connection_state="CONNECTED",
    )
    values.update(overrides)
    return TelemetryEvent(**values)  # type: ignore[arg-type]


def test_quality_detects_invalid_battery_and_duplicate() -> None:
    result = validate_event(event(battery_soc=101), {"one"})
    assert {"INVALID_BATTERY_SOC", "DUPLICATE"} == set(result.flags)
    assert quality_score([result]) == 0.0


def test_quality_detects_invalid_warning_order() -> None:
    result = validate_event(
        event(
            warning_generated_at="2026-01-01T00:00:02+00:00",
            warning_displayed_at="2026-01-01T00:00:01+00:00",
        )
    )
    assert "INVALID_WARNING_SEQUENCE" in result.flags
