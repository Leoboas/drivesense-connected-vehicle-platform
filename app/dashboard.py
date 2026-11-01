"""Local portfolio dashboard for DriveSense analytical data.

Run with: streamlit run app/dashboard.py
Set DRIVESENSE_DASHBOARD_DATA to a JSONL or Parquet file/prefix when needed.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

DEFAULT_DATA = "data/samples/dashboard-demo.jsonl"
REQUIRED_INPUT_COLUMNS = {
    "event_id",
    "vehicle_id",
    "trip_id",
    "timestamp",
    "latitude",
    "longitude",
    "speed_kph",
    "battery_soc",
    "signal_dbm",
    "latency_ms",
    "connection_state",
}
LEGACY_DEFAULTS: dict[str, object] = {
    "warning_generated_at": None,
    "warning_displayed_at": None,
    "object_detected": False,
    "scenario": "LEGACY_SAO_PAULO",
    "route_id": "legacy-sp-urban",
    "route_segment": "SAO_PAULO_METRO",
    "region_type": "URBAN",
    "offline_duration_s": 0,
    "reconnection_count": 0,
    "sync_duration_ms": 0,
    "packet_loss_pct": 0.0,
    "bytes_buffered": 0,
    "screen_id": "UNKNOWN",
    "interaction_type": "NONE",
    "warning_level": "NONE",
    "energy_consumption_kwh": 0.0,
    "range_estimate_km": 0.0,
    "tire_pressure_status": "UNKNOWN",
    "battery_temperature_c": 25.0,
    "late_arrival_seconds": 0,
    "retry_count": 0,
    "processing_latency_ms": 0,
    "road_class": "UNKNOWN",
    "weather_condition": "UNKNOWN",
    "road_surface": "UNKNOWN",
    "traffic_level": "UNKNOWN",
}


def relation_for(path: str) -> str:
    """Return a DuckDB relation expression only for supported local inputs."""
    normalized = path.replace("\\", "/").replace("'", "''")
    if normalized.endswith(".jsonl") or normalized.endswith(".json"):
        return f"read_json_auto('{normalized}')"
    if normalized.endswith(".parquet") or normalized.endswith("/*.parquet"):
        return f"read_parquet('{normalized}', hive_partitioning=true)"
    raise ValueError("Use a .jsonl, .json, .parquet or /*.parquet input path.")


@st.cache_data(show_spinner=False)
def load_rows(path: str):  # type: ignore[no-untyped-def]
    """Load current or legacy Silver data into the dashboard's display contract."""
    connection = duckdb.connect()
    source = relation_for(path)
    rows = connection.sql(f"SELECT * FROM {source}").df()
    missing = REQUIRED_INPUT_COLUMNS.difference(rows.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Input is missing required telemetry columns: {missing_columns}.")
    for column, default in LEGACY_DEFAULTS.items():
        if column not in rows:
            rows[column] = default
    rows["event_timestamp"] = pd.to_datetime(rows["timestamp"], errors="coerce", utc=True)
    warning_generated = pd.to_datetime(rows["warning_generated_at"], errors="coerce", utc=True)
    warning_displayed = pd.to_datetime(rows["warning_displayed_at"], errors="coerce", utc=True)
    rows["warning_latency_ms"] = (warning_displayed - warning_generated).dt.total_seconds() * 1000
    rows["data_quality_flag"] = "VALID"
    rows.loc[(rows["battery_soc"] < 0) | (rows["battery_soc"] > 100), "data_quality_flag"] = (
        "INVALID_BATTERY_SOC"
    )
    rows.loc[rows["speed_kph"] < 0, "data_quality_flag"] = "INVALID_SPEED"
    rows.loc[rows["event_timestamp"].isna(), "data_quality_flag"] = "INVALID_TIMESTAMP"
    return rows


def show_dashboard(data) -> None:  # type: ignore[no-untyped-def]
    selected_scenarios = st.sidebar.multiselect(
        "Geographic scenarios",
        options=sorted(data["scenario"].unique()),
        default=sorted(data["scenario"].unique()),
    )
    data = data[data["scenario"].isin(selected_scenarios)]
    if data.empty:
        st.info("Select at least one geographic scenario.")
        return
    total_events = len(data)
    vehicle_count = data["vehicle_id"].nunique()
    trip_count = data["trip_id"].nunique()
    invalid_count = int((data["data_quality_flag"] != "VALID").sum())

    executive, overview, connectivity, hmi, quality, route = st.tabs(
        [
            "Premium mobility",
            "Vehicle overview",
            "Connectivity",
            "HMI / proximity",
            "Data quality",
            "Route intelligence",
        ]
    )

    with executive:
        detected_events = data[data["object_detected"]]
        warning_delivery_rate = (
            detected_events["warning_displayed_at"].notna().mean()
            if not detected_events.empty
            else 1.0
        )
        connected_rate = (data["connection_state"] == "CONNECTED").mean()
        hands_free_rate = data["interaction_type"].isin(["VOICE", "STEERING_WHEEL"]).mean()
        vehicle_health_rate = (
            (data["tire_pressure_status"] != "LOW") & data["battery_temperature_c"].between(15, 45)
        ).mean()
        a, b, c, d = st.columns(4)
        a.metric("Safety-warning delivery", f"{warning_delivery_rate:.1%}")
        b.metric("Connected journey continuity", f"{connected_rate:.1%}")
        c.metric("Low-distraction interaction", f"{hands_free_rate:.1%}")
        d.metric("Vehicle health within range", f"{vehicle_health_rate:.1%}")
        st.subheader("Connected premium mobility — executive lens")
        st.caption(
            "Independent portfolio view using synthetic telemetry. It is not a BMW product, "
            "dataset, or performance claim."
        )
        st.dataframe(
            [
                {
                    "Pillar": "Safety and confidence",
                    "Evidence": "Warning delivery, response latency and vehicle-health signals",
                    "Decision enabled": "Prioritise safety-critical experience defects",
                },
                {
                    "Pillar": "Effortless digital experience",
                    "Evidence": "Voice/steering-wheel interactions and HMI warning context",
                    "Decision enabled": "Reduce driver distraction in digital journeys",
                },
                {
                    "Pillar": "Journey continuity",
                    "Evidence": "Coverage, packet loss, buffering and reconnection behaviour",
                    "Decision enabled": "Protect navigation and services during weak connectivity",
                },
                {
                    "Pillar": "Electric mobility readiness",
                    "Evidence": "Energy per event, range estimate and battery temperature",
                    "Decision enabled": (
                        "Surface energy and range context without overstating precision"
                    ),
                },
            ],
            hide_index=True,
            use_container_width=True,
        )

    with overview:
        a, b, c, d = st.columns(4)
        a.metric("Events", f"{total_events:,}")
        b.metric("Vehicles", f"{vehicle_count:,}")
        c.metric("Trips", f"{trip_count:,}")
        d.metric("Average speed", f"{data['speed_kph'].mean():.1f} km/h")
        e, f, g = st.columns(3)
        e.metric("Average energy", f"{data['energy_consumption_kwh'].mean():.3f} kWh/event")
        f.metric("Estimated range", f"{data['range_estimate_km'].mean():.0f} km")
        g.metric("Low tire-pressure events", f"{(data['tire_pressure_status'] == 'LOW').sum():,}")
        st.subheader("Synthetic vehicle locations by declared road and trail corridors")
        st.caption(
            "São Paulo–Florianópolis follows declared BR-116/BR-101 waypoints and the island "
            "bridge access; it is not a routing engine or real GPS trace."
        )
        st.map(
            data[["latitude", "longitude"]]
            .dropna()
            .rename(columns={"latitude": "lat", "longitude": "lon"})
        )
        st.subheader("Event volume by geographic scenario")
        st.bar_chart(data["scenario"].value_counts(), y_label="Events")

    with connectivity:
        a, b, c, d = st.columns(4)
        a.metric("Average latency", f"{data['latency_ms'].mean():.1f} ms")
        offline = int((data["connection_state"] == "OFFLINE").sum())
        b.metric("Offline events", f"{offline:,}")
        c.metric("Average signal", f"{data['signal_dbm'].mean():.1f} dBm")
        d.metric("Packet loss", f"{data['packet_loss_pct'].mean():.1f}%")
        e, f, g = st.columns(3)
        e.metric("Buffered data", f"{data['bytes_buffered'].sum() / 1_000_000:.2f} MB")
        f.metric("Average sync time", f"{data['sync_duration_ms'].mean():.0f} ms")
        g.metric("Reconnections", f"{data['reconnection_count'].sum():,}")
        st.subheader("Average latency over time")
        daily = (
            data.assign(event_date=data["event_timestamp"].dt.date)
            .groupby("event_date")["latency_ms"]
            .mean()
        )
        st.line_chart(daily, y_label="Average latency (ms)")
        stability = data.groupby("route_segment")["latency_ms"].mean().sort_values(ascending=False)
        st.subheader("Average latency by road or trail segment")
        st.bar_chart(stability, y_label="Average latency (ms)")

    with hmi:
        warning_events = data.dropna(subset=["warning_latency_ms"])
        a, b, c = st.columns(3)
        a.metric(
            "Warning latency P50", f"{warning_events['warning_latency_ms'].quantile(0.50):.0f} ms"
        )
        b.metric(
            "Warning latency P95", f"{warning_events['warning_latency_ms'].quantile(0.95):.0f} ms"
        )
        missing_warning_rate = (
            (data["object_detected"]) & data["warning_displayed_at"].isna()
        ).mean()
        c.metric("Missing warning rate", f"{missing_warning_rate:.2%}")
        st.subheader("Warning-latency distribution")
        latency_distribution = (
            warning_events["warning_latency_ms"].round(-1).value_counts().sort_index()
        )
        st.bar_chart(latency_distribution, y_label="Warnings")
        st.subheader("Multimedia and driver interaction context")
        st.dataframe(
            data.groupby(["screen_id", "interaction_type", "warning_level"])
            .size()
            .reset_index(name="events")
            .sort_values("events", ascending=False),
            hide_index=True,
        )

    with quality:
        a, b = st.columns(2)
        a.metric("Invalid events", f"{invalid_count:,}")
        a.metric("Data quality score", f"{(1 - invalid_count / max(total_events, 1)):.2%}")
        b.subheader("Records by data-quality rule")
        b.dataframe(
            data["data_quality_flag"]
            .value_counts()
            .rename_axis("rule")
            .reset_index(name="records"),
            hide_index=True,
        )
        st.subheader("DataOps processing health")
        st.dataframe(
            data.groupby("scenario")[
                ["late_arrival_seconds", "retry_count", "processing_latency_ms"]
            ]
            .mean()
            .reset_index(),
            hide_index=True,
        )

    with route:
        st.markdown(
            """The V1 route score is a deterministic, explainable heuristic. It balances expected
connectivity, travel time, energy use and positive elevation change; it is not a navigation
recommendation."""
        )
        offline_probability = 1 - (data["connection_state"] == "CONNECTED").mean()
        st.metric("Observed non-connected event rate", f"{offline_probability:.2%}")
        st.subheader("Route and connectivity risk by segment")
        route_risk = (
            data.assign(non_connected=data["connection_state"] != "CONNECTED")
            .groupby(["scenario", "route_segment"])
            .agg(
                non_connected_rate=("non_connected", "mean"),
                offline_duration_s=("offline_duration_s", "mean"),
                reconnections=("reconnection_count", "mean"),
            )
            .reset_index()
            .sort_values("non_connected_rate", ascending=False)
        )
        st.dataframe(route_risk, hide_index=True)
        st.subheader("Route context")
        st.dataframe(
            data.groupby(["road_class", "weather_condition", "road_surface", "traffic_level"])
            .size()
            .reset_index(name="events")
            .sort_values("events", ascending=False),
            hide_index=True,
        )
        st.info(
            "When predicted offline probability exceeds 40%, the simulated platform requests "
            "offline prefetch."
        )


def main() -> None:
    st.set_page_config(page_title="DriveSense | Connected Vehicle Platform", layout="wide")
    st.title("DriveSense Connected Vehicle Platform")
    st.caption(
        "Portfolio dashboard — synthetic data only; it is not an operational vehicle control plane."
    )
    default_path = os.getenv("DRIVESENSE_DASHBOARD_DATA", DEFAULT_DATA)
    data_path = st.sidebar.text_input("JSONL or Parquet path", default_path)
    if not Path(data_path).exists() and "*" not in data_path:
        st.warning(
            f"Input not found: {data_path}. Generate the DEMO_SMALL data or select a local "
            "Parquet file."
        )
        return
    try:
        show_dashboard(load_rows(data_path))
    except Exception as exc:  # Dashboard boundary: preserve an actionable local error.
        st.error(f"Unable to load dashboard data: {exc}")


if __name__ == "__main__":
    main()
