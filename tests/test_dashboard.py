import json

import pandas as pd

from app.dashboard import (
    brand_css_variables,
    dashboard_hero,
    experience_status,
    latency_by_minute,
    load_rows,
    relation_for,
    vehicle_label,
    vehicle_model_for,
    vehicle_system_map,
    vehicle_system_view,
    vehicle_timeline,
)


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
    assert rows.loc[0, "vehicle_model"] == "BMW iX2 xDrive30 M Sport"
    assert rows.loc[0, "data_quality_flag"] == "VALID"


def test_vehicle_label_maps_synthetic_fleet_identifiers_to_brazilian_model_names() -> None:
    assert vehicle_model_for("vehicle-0000") == "BMW iX1 xDrive30 M Sport"
    assert vehicle_label("vehicle-0000") == "BMW iX1 xDrive30 M Sport · vehicle-0000"


def test_vehicle_system_map_marks_connected_vehicle_subsystems() -> None:
    figure = vehicle_system_map(
        pd.Series(
            {
                "connection_state": "DEGRADED",
                "tire_pressure_status": "NORMAL",
                "battery_temperature_c": 30.0,
                "screen_id": "NAVIGATION",
            }
        )
    )

    assert len(figure.data) == 1
    assert len(figure.layout.shapes) == 1


def test_vehicle_system_view_renders_a_top_down_vehicle_with_event_status() -> None:
    view = vehicle_system_view(
        pd.Series(
            {
                "connection_state": "OFFLINE",
                "tire_pressure_status": "LOW",
                "battery_temperature_c": 40.0,
                "screen_id": "NAVIGATION",
            }
        ),
        "BMW iX1 xDrive30 M Sport",
    )

    assert "Connected vehicle systems map" in view
    assert "OFFLINE" in view
    assert "BMW iX1 xDrive30 M Sport" in view


def test_experience_status_uses_clear_executive_thresholds() -> None:
    assert experience_status(0.99) == "EXCEPTIONAL"
    assert experience_status(0.90) == "STABLE"
    assert experience_status(0.89) == "ATTENTION"


def test_brand_css_variables_exposes_editable_tokens() -> None:
    stylesheet = brand_css_variables()
    assert "--drivesense-accent: #58b7ff;" in stylesheet
    assert "DriveSense Mobility Intelligence" not in stylesheet


def test_dashboard_hero_renders_brand_tokens_without_string_format_errors() -> None:
    hero = dashboard_hero()

    assert "CONNECTED VEHICLE ANALYTICS" in hero
    assert "DriveSense Mobility Intelligence" in hero


def test_latency_by_minute_keeps_multiple_observations_from_a_single_day() -> None:
    data = pd.DataFrame(
        {
            "event_timestamp": pd.to_datetime(
                ["2026-01-01T00:00:10Z", "2026-01-01T00:00:50Z", "2026-01-01T00:02:00Z"]
            ),
            "latency_ms": [100.0, 200.0, 300.0],
        }
    )

    result = latency_by_minute(data)

    assert result["average_latency_ms"].tolist() == [150.0, 300.0]


def test_vehicle_timeline_orders_one_vehicle_events() -> None:
    data = pd.DataFrame(
        {
            "vehicle_id": ["vehicle-1", "vehicle-2", "vehicle-1"],
            "event_timestamp": pd.to_datetime(
                ["2026-01-01T00:02:00Z", "2026-01-01T00:01:00Z", "2026-01-01T00:01:00Z"]
            ),
        }
    )

    result = vehicle_timeline(data, "vehicle-1")

    assert result["event_timestamp"].tolist() == sorted(result["event_timestamp"].tolist())
