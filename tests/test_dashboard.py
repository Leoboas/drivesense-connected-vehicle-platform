import json

from app.dashboard import experience_status, load_rows, relation_for


def test_relation_for_accepts_only_local_supported_dashboard_formats() -> None:
    assert relation_for("data/samples/dashboard-demo.jsonl") == (
        "read_json_auto('data/samples/dashboard-demo.jsonl')"
    )
    assert relation_for("data/silver/*.parquet") == (
        "read_parquet('data/silver/*.parquet', hive_partitioning=true)"
    )


def test_relation_for_escapes_a_path_and_rejects_unsupported_inputs() -> None:
    assert relation_for("data/driver's-demo.jsonl") == (
        "read_json_auto('data/driver''s-demo.jsonl')"
    )
    try:
        relation_for("data/samples/dashboard.csv")
    except ValueError as error:
        assert ".jsonl" in str(error)
    else:
        raise AssertionError("Unsupported dashboard input must be rejected.")


def test_load_rows_adapts_a_legacy_silver_record(tmp_path) -> None:  # type: ignore[no-untyped-def]
    legacy = {
        "event_id": "event-1",
        "vehicle_id": "vehicle-1",
        "trip_id": "trip-1",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "latitude": -23.55,
        "longitude": -46.63,
        "speed_kph": 45.0,
        "battery_soc": 70.0,
        "signal_dbm": -80.0,
        "latency_ms": 80.0,
        "connection_state": "CONNECTED",
    }
    path = tmp_path / "legacy.jsonl"
    path.write_text(json.dumps(legacy) + "\n", encoding="utf-8")

    load_rows.clear()
    rows = load_rows(str(path))

    assert rows.loc[0, "energy_consumption_kwh"] == 0.0
    assert rows.loc[0, "tire_pressure_status"] == "UNKNOWN"
    assert rows.loc[0, "scenario"] == "LEGACY_SAO_PAULO"
    assert rows.loc[0, "data_quality_flag"] == "VALID"


def test_experience_status_uses_clear_executive_thresholds() -> None:
    assert experience_status(0.99) == "EXCEPTIONAL"
    assert experience_status(0.90) == "STABLE"
    assert experience_status(0.89) == "ATTENTION"
