from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from drivesense.models import TelemetryEvent


@dataclass(frozen=True)
class HmiMetrics:
    observed_warnings: int
    missing_warnings: int
    false_warnings: int
    missing_warning_rate: float
    false_warning_rate: float
    generation_latency_p95_ms: float | None
    display_latency_p95_ms: float | None
    end_to_end_latency_p95_ms: float | None
    threshold_violations: int


def _milliseconds(start: str, end: str) -> float:
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() * 1000


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentile)
    return round(ordered[index], 2)


def hmi_metrics(events: list[TelemetryEvent], latency_threshold_ms: float = 500) -> HmiMetrics:
    """Classify missing/false HMI warnings without treating null as an event."""
    detected = [event for event in events if event.object_detected]
    missing = [event for event in detected if event.warning_displayed_at is None]
    warning_events = [event for event in events if event.warning_displayed_at is not None]
    false = [event for event in warning_events if not event.object_detected]
    generation = [
        _milliseconds(event.timestamp, event.warning_generated_at)
        for event in detected
        if event.warning_generated_at is not None
    ]
    display = [
        _milliseconds(event.warning_generated_at, event.warning_displayed_at)
        for event in detected
        if event.warning_generated_at is not None and event.warning_displayed_at is not None
    ]
    end_to_end = [
        _milliseconds(event.timestamp, event.warning_displayed_at)
        for event in detected
        if event.warning_displayed_at is not None
    ]
    return HmiMetrics(
        observed_warnings=len(warning_events),
        missing_warnings=len(missing),
        false_warnings=len(false),
        missing_warning_rate=round(len(missing) / len(detected), 4) if detected else 0.0,
        false_warning_rate=round(len(false) / len(warning_events), 4) if warning_events else 0.0,
        generation_latency_p95_ms=_percentile(generation, 0.95),
        display_latency_p95_ms=_percentile(display, 0.95),
        end_to_end_latency_p95_ms=_percentile(end_to_end, 0.95),
        threshold_violations=sum(value > latency_threshold_ms for value in end_to_end),
    )
