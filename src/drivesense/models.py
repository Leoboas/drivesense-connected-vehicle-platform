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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def occurred_at(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)
