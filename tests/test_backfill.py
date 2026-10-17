import json
from pathlib import Path

import pytest

from drivesense.reprocessing.backfill import BackfillScope, reprocess_jsonl


def payload(event_id: str, **overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
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
        "latency_ms": 20.0,
        "connection_state": "CONNECTED",
    }
    item.update(overrides)
    return item


def test_backfill_is_scoped_deduplicated_and_reproducible(tmp_path: Path) -> None:
    source = tmp_path / "bronze.jsonl"
    target = tmp_path / "gold.jsonl"
    source.write_text(
        "\n".join(
            json.dumps(item)
            for item in [payload("one"), payload("one"), payload("two", vehicle_id="v2")]
        )
    )
    result = reprocess_jsonl(
        source, target, BackfillScope(vehicle_id="v1"), quarantine_path=tmp_path / "q.jsonl"
    )
    assert (result.scanned, result.matched, result.written, result.duplicates) == (3, 2, 1, 1)
    with pytest.raises(FileExistsError):
        reprocess_jsonl(source, target, BackfillScope(), quarantine_path=tmp_path / "q.jsonl")
    rerun = reprocess_jsonl(
        source,
        target,
        BackfillScope(vehicle_id="v1"),
        quarantine_path=tmp_path / "q.jsonl",
        force=True,
    )
    assert rerun.written == 1


def test_backfill_dry_run_quarantines_nothing(tmp_path: Path) -> None:
    source = tmp_path / "bronze.jsonl"
    source.write_text(json.dumps(payload("bad", schema_version="telemetry.v99")))
    quarantine = tmp_path / "quarantine.jsonl"
    result = reprocess_jsonl(
        source, tmp_path / "gold.jsonl", BackfillScope(), quarantine_path=quarantine, dry_run=True
    )
    assert result.quarantined == 1
    assert not quarantine.exists()
