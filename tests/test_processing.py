import json
from pathlib import Path

from drivesense.processing.local import process_payloads


def payload(event_id: str, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "telemetry.v2",
        "event_id": event_id,
        "vehicle_id": "v1",
        "trip_id": "t1",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "latitude": 0.0,
        "longitude": 0.0,
        "speed_kph": 20.0,
        "battery_soc": 50.0,
        "network_type": "LTE",
        "signal_dbm": -80.0,
        "latency_ms": 10.0,
        "connection_state": "CONNECTED",
    }
    value.update(overrides)
    return value


def test_processing_quarantines_contract_quality_and_duplicate_failures(tmp_path: Path) -> None:
    good = payload("good")
    accepted, metrics = process_payloads(
        [
            {**good, "future_optional_field": "ignored"},
            good,
            payload("bad", battery_soc=120),
            payload("contract", schema_version="telemetry.v3"),
        ],
        tmp_path / "quarantine.jsonl",
    )
    assert len(accepted) == 1
    assert metrics.to_dict() == {
        "events_received": 4,
        "events_processed": 1,
        "events_invalid": 3,
        "events_quarantined": 3,
        "duplicates_detected": 1,
        "late_events": 0,
        "offline_events": 0,
    }
    records = [
        json.loads(line) for line in (tmp_path / "quarantine.jsonl").read_text().splitlines()
    ]
    assert {record["rule_id"] for record in records} == {"DATA_CONTRACT", "QUALITY_RULE"}
