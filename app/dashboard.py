# ruff: noqa: E501
"""Local portfolio dashboard for DriveSense analytical data.

Run with: streamlit run app/dashboard.py
Set DRIVESENSE_DASHBOARD_DATA to a JSONL or Parquet file/prefix when needed.
"""

from __future__ import annotations

import os
from html import escape
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

DEFAULT_DATA = "data/samples/dashboard-demo.jsonl"
BRAND_TOKENS = {
    "product_name": "DriveSense Mobility Intelligence",
    "eyebrow": "CONNECTED VEHICLE ANALYTICS",
    "accent": "#58b7ff",
    "accent_deep": "#162843",
    "background": "#070b12",
    "surface": "#0b1320",
    "surface_elevated": "#18273d",
    "border": "#274363",
    "text": "#f5f8fc",
    "text_muted": "#b8c8da",
    "success": "#8de3bf",
}
BMW_BRAZIL_MODELS = (
    "BMW iX1 xDrive30 M Sport",
    "BMW iX2 xDrive30 M Sport",
    "BMW i4 eDrive40 M Sport",
    "BMW i7 xDrive60 M Sport",
    "BMW X1 sDrive20i M Sport",
    "BMW X2 xDrive20i M Sport",
    "BMW X3 30 xDrive M Sport",
    "BMW X5 xDrive50e M Sport",
    "BMW 220 M Sport",
    "BMW M135 xDrive",
)
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
    "map_match_confidence": 1.0,
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


def experience_status(rate: float) -> str:
    """Translate a product-health rate into concise executive language."""
    if rate >= 0.98:
        return "EXCEPTIONAL"
    if rate >= 0.90:
        return "STABLE"
    return "ATTENTION"


def brand_css_variables() -> str:
    """Expose the editable visual tokens as CSS custom properties."""
    tokens = "".join(
        f"--drivesense-{name.replace('_', '-')}: {value};"
        for name, value in BRAND_TOKENS.items()
        if name not in {"product_name", "eyebrow"}
    )
    return f"<style>:root {{{tokens}}}</style>"


def dashboard_hero() -> str:
    """Render the branded dashboard header from the editable product tokens."""
    return f"""
        <section class="drivesense-hero">
          <div class="drivesense-eyebrow">{escape(BRAND_TOKENS["eyebrow"])}</div>
          <h1>{escape(BRAND_TOKENS["product_name"])}</h1>
          <p>An executive product briefing for safety, digital experience, journey continuity and
          electric-mobility context. Synthetic data only; no operational vehicle control.</p>
        </section>
        """


def vehicle_model_for(vehicle_id: str) -> str:
    """Map a synthetic vehicle identifier to a current Brazilian-market model label."""
    try:
        model_index = int(vehicle_id.rsplit("-", maxsplit=1)[-1]) % len(BMW_BRAZIL_MODELS)
    except ValueError:
        return "Synthetic BMW vehicle"
    return BMW_BRAZIL_MODELS[model_index]


def vehicle_label(vehicle_id: str) -> str:
    """Keep the technical identifier visible beside the presentation model name."""
    return f"{vehicle_model_for(vehicle_id)} · {vehicle_id}"


def vehicle_system_map(current: pd.Series) -> go.Figure:
    """Create a conceptual vehicle-system map, never a physical OEM diagnostic diagram."""
    connection = str(current["connection_state"])
    connection_color = {"CONNECTED": "#8de3bf", "DEGRADED": "#ffb547", "OFFLINE": "#f45b69"}.get(
        connection, "#b8c8da"
    )
    tyre_status = str(current["tire_pressure_status"])
    tyre_color = "#f45b69" if tyre_status == "LOW" else "#8de3bf"
    battery_temperature = float(current["battery_temperature_c"])
    battery_color = "#ffb547" if battery_temperature >= 38 else "#8de3bf"
    systems = pd.DataFrame(
        [
            {
                "x": 0,
                "y": 3.6,
                "system": "Telematics / antenna",
                "status": connection,
                "color": connection_color,
            },
            {
                "x": 0,
                "y": 0,
                "system": "High-voltage battery",
                "status": f"{battery_temperature:.1f} °C",
                "color": battery_color,
            },
            {
                "x": -1.35,
                "y": -1.9,
                "system": "Tyre sensors",
                "status": tyre_status,
                "color": tyre_color,
            },
            {
                "x": 0,
                "y": 1.25,
                "system": "Multimedia / HMI",
                "status": str(current["screen_id"]),
                "color": "#58b7ff",
            },
        ]
    )
    figure = go.Figure()
    figure.add_shape(
        type="path",
        path=(
            "M 0,-3.5 C -1.25,-3.0 -1.55,-1.2 -1.45,0.5 L -1.25,2.7 "
            "C -0.9,3.5 0,4.0 0,4.0 C 0,4.0 0.9,3.5 1.25,2.7 "
            "L 1.45,0.5 C 1.55,-1.2 1.25,-3.0 0,-3.5 Z"
        ),
        fillcolor="#18273d",
        line={"color": "#58b7ff", "width": 2},
    )
    figure.add_trace(
        go.Scatter(
            x=systems["x"],
            y=systems["y"],
            mode="markers+text",
            marker={
                "size": 18,
                "color": systems["color"],
                "line": {"color": "#f5f8fc", "width": 1},
            },
            text=systems["system"],
            textposition="middle right",
            customdata=systems[["status"]],
            hovertemplate="<b>%{text}</b><br>Status: %{customdata[0]}<extra></extra>",
        )
    )
    figure.update_layout(
        height=430,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        paper_bgcolor="#0b1320",
        plot_bgcolor="#0b1320",
        font={"color": "#f5f8fc"},
        showlegend=False,
        xaxis={"visible": False, "range": [-2.6, 3.2]},
        yaxis={"visible": False, "range": [-4.1, 4.8], "scaleanchor": "x", "scaleratio": 1},
    )
    return figure


def vehicle_system_view(current: pd.Series, vehicle_model: str) -> str:
    """Render an original top-down connected-vehicle view with event-specific markers."""
    connection = str(current["connection_state"])
    tyre_status = str(current["tire_pressure_status"])
    battery_temperature = float(current["battery_temperature_c"])
    hmi = escape(str(current["screen_id"]))
    connection_color = {"CONNECTED": "#8de3bf", "DEGRADED": "#ffb547", "OFFLINE": "#f45b69"}.get(
        connection, "#58b7ff"
    )
    tyre_color = "#f45b69" if tyre_status == "LOW" else "#8de3bf"
    battery_status = "ATTENTION" if battery_temperature >= 38 else "NORMAL"
    battery_color = "#ffb547" if battery_status == "ATTENTION" else "#8de3bf"
    return f"""
    <div style="background:#0b1320;border:1px solid #274363;border-radius:16px;padding:12px;color:#f5f8fc;font-family:Arial,sans-serif;max-width:820px;margin:auto">
      <div style="font-size:13px;color:#b8c8da;margin:0 0 8px 4px">{escape(vehicle_model)} · synthetic system view</div>
      <svg viewBox="0 0 820 560" width="100%" height="500" role="img" aria-label="Connected vehicle systems map">
        <rect x="0" y="0" width="820" height="560" rx="12" fill="#070b12"/>
        <path d="M355 45 C315 70 298 138 300 220 L308 430 C311 488 340 520 410 530 C480 520 509 488 512 430 L520 220 C522 138 505 70 465 45 C435 26 385 26 355 45 Z" fill="#18273d" stroke="#58b7ff" stroke-width="4"/>
        <path d="M344 166 L476 166 L492 262 L328 262 Z" fill="#274363" stroke="#58b7ff" stroke-width="2"/>
        <path d="M327 300 L493 300 L478 438 L342 438 Z" fill="#122238" stroke="#3c6d9e" stroke-width="2"/>
        <rect x="267" y="145" width="34" height="104" rx="13" fill="#05080d" stroke="#516b87" stroke-width="2"/><rect x="519" y="145" width="34" height="104" rx="13" fill="#05080d" stroke="#516b87" stroke-width="2"/>
        <rect x="267" y="350" width="34" height="104" rx="13" fill="#05080d" stroke="#516b87" stroke-width="2"/><rect x="519" y="350" width="34" height="104" rx="13" fill="#05080d" stroke="#516b87" stroke-width="2"/>
        <rect x="356" y="314" width="108" height="95" rx="10" fill="{battery_color}" opacity="0.30" stroke="{battery_color}" stroke-width="3"/>
        <text x="410" y="354" text-anchor="middle" fill="#f5f8fc" font-size="15" font-weight="700">BATTERY</text><text x="410" y="378" text-anchor="middle" fill="#f5f8fc" font-size="13">{battery_temperature:.1f} C</text>
        <rect x="365" y="198" width="90" height="35" rx="8" fill="#0b1320" stroke="#58b7ff" stroke-width="2"/><text x="410" y="221" text-anchor="middle" fill="#f5f8fc" font-size="12">HMI · {hmi}</text>
        <circle cx="410" cy="95" r="15" fill="{connection_color}" stroke="#f5f8fc" stroke-width="2"/><path d="M410 80 L410 55 M395 65 Q410 48 425 65" fill="none" stroke="{connection_color}" stroke-width="3"/>
        <circle cx="284" cy="196" r="10" fill="{tyre_color}"/><circle cx="536" cy="196" r="10" fill="{tyre_color}"/><circle cx="284" cy="402" r="10" fill="{tyre_color}"/><circle cx="536" cy="402" r="10" fill="{tyre_color}"/>
        <line x1="425" y1="95" x2="650" y2="85" stroke="{connection_color}" stroke-width="2"/><text x="660" y="80" fill="#f5f8fc" font-size="16" font-weight="700">Telematics</text><text x="660" y="104" fill="{connection_color}" font-size="15">{escape(connection)}</text>
        <line x1="464" y1="360" x2="650" y2="320" stroke="{battery_color}" stroke-width="2"/><text x="660" y="316" fill="#f5f8fc" font-size="16" font-weight="700">High-voltage battery</text><text x="660" y="340" fill="{battery_color}" font-size="15">{battery_status}</text>
        <line x1="294" y1="402" x2="160" y2="430" stroke="{tyre_color}" stroke-width="2"/><text x="40" y="425" fill="#f5f8fc" font-size="16" font-weight="700">Tyre sensors</text><text x="40" y="449" fill="{tyre_color}" font-size="15">{escape(tyre_status)}</text>
        <line x1="365" y1="215" x2="150" y2="190" stroke="#58b7ff" stroke-width="2"/><text x="40" y="185" fill="#f5f8fc" font-size="16" font-weight="700">Multimedia / HMI</text><text x="40" y="209" fill="#58b7ff" font-size="15">{hmi}</text>
      </svg>
      <div style="color:#b8c8da;font-size:12px;padding:0 4px 6px">Original conceptual visual. Statuses are synthetic telemetry context, not a physical OEM diagnostic diagram.</div>
    </div>
    """


def maintenance_history(current: pd.Series) -> pd.DataFrame:
    """Provide an explicitly synthetic service-review narrative for the selected scenario."""
    event_time = pd.Timestamp(current["event_timestamp"])
    return pd.DataFrame(
        [
            {
                "Date": event_time - pd.Timedelta(days=180),
                "Review": "Delivery inspection",
                "Status": "COMPLETED",
            },
            {
                "Date": event_time - pd.Timedelta(days=90),
                "Review": "Connected-services health check",
                "Status": "COMPLETED",
            },
            {
                "Date": event_time,
                "Review": "Journey telemetry review",
                "Status": str(current["connection_state"]),
            },
            {
                "Date": event_time + pd.Timedelta(days=90),
                "Review": "Preventive service window",
                "Status": "PLANNED",
            },
        ]
    )


def connectivity_incident_map(timeline: pd.DataFrame) -> go.Figure:
    """Plot a readable 2D coordinate view for synthetic connectivity incidents."""
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=timeline["longitude"],
            y=timeline["latitude"],
            mode="markers",
            name="Journey context",
            marker={"size": 6, "color": "#516b87", "opacity": 0.45},
            hoverinfo="skip",
        )
    )
    for state, color in (("DEGRADED", "#ffb547"), ("OFFLINE", "#f45b69")):
        subset = timeline[timeline["connection_state"] == state]
        figure.add_trace(
            go.Scatter(
                x=subset["longitude"],
                y=subset["latitude"],
                mode="markers",
                name=state,
                marker={"size": 14, "color": color, "line": {"color": "#f5f8fc", "width": 1}},
                customdata=subset[
                    [
                        "event_timestamp",
                        "route_segment",
                        "road_class",
                        "offline_duration_s",
                        "packet_loss_pct",
                        "latency_ms",
                    ]
                ],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>Longitude: %{x:.6f}°<br>Latitude: %{y:.6f}°"
                    "<br>Event: %{customdata[0]}<br>Segment: %{customdata[1]}"
                    "<br>Road: %{customdata[2]}<br>Offline: %{customdata[3]} s"
                    "<br>Packet loss: %{customdata[4]:.1f}%<br>Latency: %{customdata[5]:.1f} ms"
                    "<extra></extra>"
                ),
            )
        )
    figure.update_layout(
        height=520,
        margin={"l": 10, "r": 10, "t": 35, "b": 10},
        paper_bgcolor="#0b1320",
        plot_bgcolor="#0b1320",
        font={"color": "#f5f8fc"},
        legend={"orientation": "h", "y": 1.08},
        xaxis={"title": "Longitude (°)", "gridcolor": "#274363", "zeroline": False},
        yaxis={"title": "Latitude (°)", "gridcolor": "#274363", "zeroline": False},
    )
    return figure


def latency_by_minute(data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate latency at a useful simulation-playback granularity."""
    return (
        data.dropna(subset=["event_timestamp"])
        .set_index("event_timestamp")
        .sort_index()["latency_ms"]
        .resample("min")
        .mean()
        .dropna()
        .rename("average_latency_ms")
        .reset_index()
    )


def vehicle_timeline(data: pd.DataFrame, vehicle_id: str) -> pd.DataFrame:
    """Return one vehicle's ordered synthetic journey for the digital-twin replay."""
    return (
        data[data["vehicle_id"] == vehicle_id].sort_values("event_timestamp").reset_index(drop=True)
    )


def apply_premium_theme() -> None:
    """Apply a restrained, original cockpit-inspired presentation theme."""
    st.markdown(brand_css_variables(), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .stApp {
          background: radial-gradient(
            circle at top right, var(--drivesense-accent-deep) 0%, #0a101a 35%,
            var(--drivesense-background) 100%
          );
        }
        [data-testid="stSidebar"] {
          background: var(--drivesense-surface); border-right: 1px solid var(--drivesense-border);
        }
        [data-testid="stHeader"] { background: rgba(7, 11, 18, 0.75); }
        [data-testid="stMetric"] {
          background: linear-gradient(
            145deg, var(--drivesense-surface-elevated), var(--drivesense-surface)
          );
          border: 1px solid var(--drivesense-border); border-radius: 14px; padding: 1rem;
          box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
        }
        [data-testid="stMetricLabel"] { color: var(--drivesense-text-muted); }
        [data-testid="stMetricValue"] { color: var(--drivesense-text); }
        .drivesense-hero {
          border: 1px solid var(--drivesense-border); border-radius: 18px; padding: 1.5rem 1.75rem;
          background: linear-gradient(
            110deg, var(--drivesense-accent-deep), var(--drivesense-surface)
          );
          margin: 0.25rem 0 1.25rem 0;
        }
        .drivesense-eyebrow {
          color: var(--drivesense-accent); font-size: 0.75rem; font-weight: 700;
          letter-spacing: 0.14em;
        }
        .drivesense-hero h1 { color: var(--drivesense-text); margin: 0.3rem 0; font-weight: 650; }
        .drivesense-hero p { color: var(--drivesense-text-muted); margin: 0; max-width: 58rem; }
        .drivesense-status {
          display: inline-block; border: 1px solid var(--drivesense-success); border-radius: 999px;
          color: var(--drivesense-success);
          font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; padding: 0.28rem 0.6rem;
          margin-bottom: 0.65rem;
        }
        button[data-baseweb="tab"] { color: var(--drivesense-text-muted); font-weight: 600; }
        button[data-baseweb="tab"][aria-selected="true"] {
          color: var(--drivesense-text); border-bottom-color: var(--drivesense-accent);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    rows["vehicle_model"] = rows["vehicle_id"].map(vehicle_model_for)
    rows["vehicle_label"] = rows["vehicle_id"].map(vehicle_label)
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
    st.sidebar.markdown("## DriveSense studio")
    st.sidebar.caption("Connected-vehicle analytical briefing")
    selected_scenarios = st.sidebar.multiselect(
        "Journey scenarios",
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
    connected_rate = (data["connection_state"] == "CONNECTED").mean()
    st.sidebar.markdown("---")
    st.sidebar.metric("Journey continuity", f"{connected_rate:.1%}")
    st.sidebar.metric("Data quality", f"{(1 - invalid_count / max(total_events, 1)):.1%}")

    twin, executive, overview, connectivity, hmi, quality, route = st.tabs(
        [
            "Digital twin",
            "Premium mobility",
            "Vehicle overview",
            "Connectivity",
            "HMI / proximity",
            "Data quality",
            "Route intelligence",
        ]
    )

    with twin:
        st.subheader("Vehicle digital twin — synthetic scenario replay")
        st.caption(
            "Select a synthetic vehicle and move through its captured events. This is a product "
            "simulation, not a live vehicle control interface."
        )
        selected_vehicle = st.selectbox(
            "Vehicle",
            sorted(data["vehicle_id"].unique()),
            format_func=vehicle_label,
        )
        timeline = vehicle_timeline(data, selected_vehicle)
        selected_event = st.slider(
            "Journey event",
            min_value=0,
            max_value=max(len(timeline) - 1, 0),
            value=0,
            format="%d",
        )
        current = timeline.iloc[selected_event]
        st.markdown(f"#### {current['vehicle_model']}  ")
        st.caption(f"Synthetic fleet identity · {selected_vehicle}")
        st.info(
            "Scenario estimates only: speed, battery, range and connectivity are generated "
            "telemetry values. The route is a land-based corridor, not live road, traffic, "
            "elevation or vehicle data."
        )
        a, b, c, d = st.columns(4)
        a.metric("Scenario speed", f"{current['speed_kph']:.0f} km/h")
        b.metric("Simulated battery state", f"{current['battery_soc']:.0f}%")
        c.metric("Modelled range", f"{current['range_estimate_km']:.0f} km")
        d.metric("Synthetic connection", str(current["connection_state"]))
        left, right = st.columns([1.25, 1])
        with left:
            st.subheader("Journey condition replay")
            replay_metrics = timeline.set_index("event_timestamp")[
                ["battery_soc", "latency_ms", "signal_dbm"]
            ]
            st.line_chart(replay_metrics, y_label="Vehicle and service signals")
        with right:
            st.subheader("Multimedia and vehicle context")
            st.markdown(
                f"**Screen:** {current['screen_id']}  \n"
                f"**Interaction:** {current['interaction_type']}  \n"
                f"**Road:** {current['road_class']} · {current['road_surface']}  \n"
                f"**Conditions:** {current['weather_condition']} · "
                f"{current['traffic_level']} traffic"
            )
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Signal": "Battery temperature",
                            "Value": f"{current['battery_temperature_c']:.1f} °C",
                        },
                        {"Signal": "Tyre pressure", "Value": current["tire_pressure_status"]},
                        {"Signal": "Packet loss", "Value": f"{current['packet_loss_pct']:.1f}%"},
                        {
                            "Signal": "Map-match confidence",
                            "Value": f"{current['map_match_confidence']:.0%}",
                        },
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
        st.subheader("Vehicle systems cockpit view")
        st.caption(
            "An original top-down vehicle visual for the selected synthetic event. It surfaces "
            "telematics, battery, tyre and HMI context; it is not an OEM diagnostic diagram."
        )
        components.html(vehicle_system_view(current, str(current["vehicle_model"])), height=570)
        st.subheader("Review history")
        st.caption(
            "Synthetic service-review narrative for this portfolio scenario; not a vehicle record."
        )
        st.dataframe(maintenance_history(current), hide_index=True, use_container_width=True)
        with st.expander("Technical 3D vehicle-state space"):
            st.caption(
                "Each point is an event. Position combines battery state, latency and energy; "
                "colour shows connection state and point size represents speed."
            )
            figure = px.scatter_3d(
                timeline,
                x="battery_soc",
                y="latency_ms",
                z="energy_consumption_kwh",
                color="connection_state",
                size="speed_kph",
                size_max=18,
                hover_data=[
                    "event_timestamp",
                    "screen_id",
                    "interaction_type",
                    "weather_condition",
                    "road_class",
                ],
                labels={
                    "battery_soc": "Battery state (%)",
                    "latency_ms": "Latency (ms)",
                    "energy_consumption_kwh": "Energy (kWh/event)",
                },
                color_discrete_map={
                    "CONNECTED": "#58b7ff",
                    "DEGRADED": "#ffb547",
                    "OFFLINE": "#f45b69",
                },
            )
            figure.update_layout(
                height=560,
                margin={"l": 0, "r": 0, "t": 20, "b": 0},
                paper_bgcolor="#0b1320",
                font={"color": "#f5f8fc"},
                scene={"bgcolor": "#0b1320"},
            )
            st.plotly_chart(figure, use_container_width=True, theme=None)
        with st.expander("Connectivity incident corridor map"):
            incidents = timeline[timeline["connection_state"].isin(["DEGRADED", "OFFLINE"])]
            st.caption(
                "A 2D geographic-coordinate view: grey points are journey context, while amber "
                "and red points locate synthetic DEGRADED and OFFLINE events precisely."
            )
            if incidents.empty:
                st.info("No DEGRADED or OFFLINE events were generated for this selected journey.")
            else:
                st.plotly_chart(
                    connectivity_incident_map(timeline), use_container_width=True, theme=None
                )

    with executive:
        detected_events = data[data["object_detected"]]
        warning_delivery_rate = (
            detected_events["warning_displayed_at"].notna().mean()
            if not detected_events.empty
            else 1.0
        )
        hands_free_rate = data["interaction_type"].isin(["VOICE", "STEERING_WHEEL"]).mean()
        vehicle_health_rate = (
            (data["tire_pressure_status"] != "LOW") & data["battery_temperature_c"].between(15, 45)
        ).mean()
        a, b, c, d = st.columns(4)
        a.metric("Safety-warning delivery", f"{warning_delivery_rate:.1%}")
        b.metric("Connected journey continuity", f"{connected_rate:.1%}")
        c.metric("Low-distraction interaction", f"{hands_free_rate:.1%}")
        d.metric("Vehicle health within range", f"{vehicle_health_rate:.1%}")
        st.markdown(
            (
                '<span class="drivesense-status">JOURNEY STATUS · '
                f"{experience_status(connected_rate)}</span>"
            ),
            unsafe_allow_html=True,
        )
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
        st.line_chart(
            latency_by_minute(data).set_index("event_timestamp"),
            y="average_latency_ms",
            y_label="Average latency (ms)",
        )
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
    st.set_page_config(
        page_title="DriveSense | Connected Vehicle Platform",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_premium_theme()
    st.markdown(dashboard_hero(), unsafe_allow_html=True)
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
