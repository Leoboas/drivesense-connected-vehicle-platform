from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from drivesense.models import TelemetryEvent


@dataclass(frozen=True)
class QualityResult:
    event_id: str
    flags: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not any(flag.startswith("INVALID") or flag == "DUPLICATE" for flag in self.flags)


def validate_event(event: TelemetryEvent, seen_event_ids: set[str] | None = None) -> QualityResult:
    flags: list[str] = []
    if not event.vehicle_id or not event.timestamp:
        flags.append("INVALID_REQUIRED_FIELD")
    try:
        datetime.fromisoformat(event.timestamp)
    except ValueError:
        flags.append("INVALID_TIMESTAMP")
    if event.speed_kph < 0:
        flags.append("INVALID_SPEED")
    if not 0 <= event.battery_soc <= 100:
        flags.append("INVALID_BATTERY_SOC")
    if not -140 <= event.signal_dbm <= -30:
        flags.append("SUSPICIOUS_SIGNAL_DBM")
    if event.warning_generated_at and event.warning_displayed_at:
        if event.warning_displayed_at < event.warning_generated_at:
            flags.append("INVALID_WARNING_SEQUENCE")
    if seen_event_ids is not None and event.event_id in seen_event_ids:
        flags.append("DUPLICATE")
    return QualityResult(event.event_id, tuple(flags))


def quality_score(results: list[QualityResult]) -> float:
    if not results:
        return 100.0
    return round(100 * sum(result.is_valid for result in results) / len(results), 2)


def duplicate_event_ids(events: list[TelemetryEvent]) -> set[str]:
    counts = Counter(event.event_id for event in events)
    return {event_id for event_id, count in counts.items() if count > 1}
