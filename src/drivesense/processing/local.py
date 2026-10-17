from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

from drivesense.contracts.validation import validate_telemetry
from drivesense.models import TelemetryEvent
from drivesense.observability.logging import configure_structured_logging, log_event
from drivesense.quality.quarantine import quarantine_payload
from drivesense.quality.rules import validate_event

MODEL_FIELDS = frozenset(field.name for field in fields(TelemetryEvent))


@dataclass(frozen=True)
class ProcessingMetrics:
    events_received: int = 0
    events_processed: int = 0
    events_invalid: int = 0
    events_quarantined: int = 0
    duplicates_detected: int = 0
    late_events: int = 0
    offline_events: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def process_payloads(
    payloads: list[dict[str, Any]], quarantine_path: Path, correlation_id: str = "local-run"
) -> tuple[list[TelemetryEvent], ProcessingMetrics]:
    logger = configure_structured_logging()
    accepted: list[TelemetryEvent] = []
    seen: set[str] = set()
    metrics = ProcessingMetrics(events_received=len(payloads))
    latest_by_trip: dict[tuple[str, str], str] = {}
    for payload in payloads:
        contract = validate_telemetry(payload)
        event_id = payload.get("event_id") if isinstance(payload.get("event_id"), str) else None
        common = {
            "component": "local-processing",
            "correlation_id": correlation_id,
            "event_id": event_id,
            "schema_version": contract.schema_version,
        }
        if not contract.accepted:
            quarantine_payload(quarantine_path, payload, ";".join(contract.errors), "DATA_CONTRACT")
            metrics = ProcessingMetrics(
                **{
                    **metrics.to_dict(),
                    "events_invalid": metrics.events_invalid + 1,
                    "events_quarantined": metrics.events_quarantined + 1,
                }
            )
            log_event(logger, "event quarantined", status="QUARANTINED", **common)
            continue
        event = TelemetryEvent(
            **{key: value for key, value in payload.items() if key in MODEL_FIELDS}
        )
        quality = validate_event(event, seen)
        if not quality.is_valid:
            quarantine_payload(quarantine_path, payload, ";".join(quality.flags), "QUALITY_RULE")
            duplicate = int("DUPLICATE" in quality.flags)
            metrics = ProcessingMetrics(
                **{
                    **metrics.to_dict(),
                    "events_invalid": metrics.events_invalid + 1,
                    "events_quarantined": metrics.events_quarantined + 1,
                    "duplicates_detected": metrics.duplicates_detected + duplicate,
                }
            )
            log_event(logger, "event quarantined", status="QUARANTINED", **common)
            continue
        trip_key = (event.vehicle_id, event.trip_id)
        late = trip_key in latest_by_trip and event.timestamp < latest_by_trip[trip_key]
        latest_by_trip[trip_key] = max(
            event.timestamp, latest_by_trip.get(trip_key, event.timestamp)
        )
        seen.add(event.event_id)
        accepted.append(event)
        metrics = ProcessingMetrics(
            **{
                **metrics.to_dict(),
                "events_processed": metrics.events_processed + 1,
                "late_events": metrics.late_events + int(late),
                "offline_events": metrics.offline_events + int(event.connection_state == "OFFLINE"),
            }
        )
        log_event(
            logger,
            "event processed",
            status="PROCESSED",
            vehicle_id=event.vehicle_id,
            trip_id=event.trip_id,
            **common,
        )
    return accepted, metrics
