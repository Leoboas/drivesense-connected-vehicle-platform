from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TelemetryEvent:
    event_id: str
    vehicle_id: str
    trip_id: str
    timestamp: str
    latitude: float
    longitude: float
    speed_kph: float
    battery_soc: float
    network_type: str
    signal_dbm: float
    latency_ms: float
    connection_state: str
    proximity_front_cm: float | None = None
    object_detected: bool = False
    warning_generated_at: str | None = None
    warning_displayed_at: str | None = None
    schema_version: str = "telemetry.v2"
    scenario: str = "SAO_PAULO_URBAN"
    route_id: str = "sp-urban"
    route_segment: str = "SAO_PAULO_METRO"
    region_type: str = "URBAN"
    offline_duration_s: int = 0
    reconnection_count: int = 0
    sync_duration_ms: int = 0
    packet_loss_pct: float = 0.0
    network_provider: str = "SYNTHETIC_PROVIDER_A"
    bytes_buffered: int = 0
    road_class: str = "URBAN_ARTERIAL"
    distance_remaining_km: float = 0.0
    eta_minutes: float = 0.0
    reroute_count: int = 0
    map_match_confidence: float = 1.0
    screen_id: str = "NAVIGATION"
    interaction_type: str = "NONE"
    warning_level: str = "NONE"
    driver_action: str = "NONE"
    driver_response_time_ms: int | None = None
    battery_temperature_c: float = 25.0
    energy_consumption_kwh: float = 0.0
    range_estimate_km: float = 0.0
    tire_pressure_status: str = "NORMAL"
    vehicle_state: str = "DRIVING"
    ingested_at: str = ""
    late_arrival_seconds: int = 0
    retry_count: int = 0
    processing_latency_ms: int = 0
    weather_condition: str = "CLEAR"
    road_surface: str = "DRY"
    traffic_level: str = "MODERATE"
    visibility_level: str = "GOOD"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def occurred_at(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)
