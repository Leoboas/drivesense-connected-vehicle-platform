from pathlib import Path

from drivesense.contracts.validation import validate_telemetry
from drivesense.quality.quarantine import quarantine_payload


def telemetry_payload(version: str = "telemetry.v1") -> dict[str, object]:
    return {
        "schema_version": version,
        "event_id": "event-1",
        "vehicle_id": "vehicle-1",
        "trip_id": "trip-1",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "latitude": -23.5,
        "longitude": -46.6,
        "speed_kph": 42.0,
        "battery_soc": 80.0,
        "network_type": "LTE",
        "signal_dbm": -80.0,
        "latency_ms": 50.0,
        "connection_state": "CONNECTED",
    }


def test_contract_accepts_v1_v2_and_unknown_optional_fields() -> None:
    v1 = telemetry_payload()
    v2 = telemetry_payload("telemetry.v2")
    v2["battery_temperature_c"] = 24.5
    v2["future_optional_field"] = "tolerated"
    assert validate_telemetry(v1).accepted
    assert validate_telemetry(v2).accepted


def test_contract_rejects_invalid_version_and_missing_required_field() -> None:
    invalid_version = telemetry_payload("telemetry.v9")
    missing_vehicle = telemetry_payload()
    del missing_vehicle["vehicle_id"]
    assert validate_telemetry(invalid_version).errors == ("UNSUPPORTED_SCHEMA_VERSION",)
    assert "MISSING_REQUIRED:vehicle_id" in validate_telemetry(missing_vehicle).errors


def test_quarantine_preserves_original_payload(tmp_path: Path) -> None:
    payload = telemetry_payload()
    record = quarantine_payload(
        tmp_path / "quarantine.jsonl", payload, "required vehicle is absent", "MISSING_REQUIRED"
    )
    assert record.original_payload == payload
    assert '"rule_id": "MISSING_REQUIRED"' in (tmp_path / "quarantine.jsonl").read_text()
