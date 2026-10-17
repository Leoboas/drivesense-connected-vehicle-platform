from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

TELEMETRY_REQUIRED = frozenset(
    {
        "schema_version",
        "event_id",
        "vehicle_id",
        "trip_id",
        "timestamp",
        "latitude",
        "longitude",
        "speed_kph",
        "battery_soc",
        "network_type",
        "signal_dbm",
        "latency_ms",
        "connection_state",
    }
)
STRING_FIELDS = frozenset({"event_id", "vehicle_id", "trip_id", "timestamp"})
NUMBER_FIELDS = frozenset(
    {"latitude", "longitude", "speed_kph", "battery_soc", "signal_dbm", "latency_ms"}
)
NETWORK_TYPES = frozenset({"5G", "LTE", "3G", "OFFLINE"})
CONNECTION_STATES = frozenset({"CONNECTED", "DEGRADED", "OFFLINE", "RECOVERY"})


@dataclass(frozen=True)
class ContractResult:
    accepted: bool
    schema_version: str | None
    errors: tuple[str, ...]


def validate_telemetry(payload: dict[str, Any]) -> ContractResult:
    version = payload.get("schema_version")
    errors: list[str] = []
    if version not in {"telemetry.v1", "telemetry.v2"}:
        errors.append("UNSUPPORTED_SCHEMA_VERSION")
        return ContractResult(False, version if isinstance(version, str) else None, tuple(errors))
    for field in sorted(TELEMETRY_REQUIRED - payload.keys()):
        errors.append(f"MISSING_REQUIRED:{field}")
    for field in STRING_FIELDS:
        if field in payload and (not isinstance(payload[field], str) or not payload[field]):
            errors.append(f"INVALID_TYPE:{field}")
    for field in NUMBER_FIELDS:
        if field in payload and (
            not isinstance(payload[field], int | float) or isinstance(payload[field], bool)
        ):
            errors.append(f"INVALID_TYPE:{field}")
    if payload.get("network_type") not in NETWORK_TYPES:
        errors.append("INVALID_ENUM:network_type")
    if payload.get("connection_state") not in CONNECTION_STATES:
        errors.append("INVALID_ENUM:connection_state")
    if isinstance(payload.get("timestamp"), str):
        try:
            datetime.fromisoformat(payload["timestamp"])
        except ValueError:
            errors.append("INVALID_TIMESTAMP")
    return ContractResult(not errors, version, tuple(errors))
