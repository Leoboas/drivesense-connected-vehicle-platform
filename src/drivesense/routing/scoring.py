from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteSegment:
    segment_id: str
    distance_km: float
    travel_time_minutes: float
    elevation_change_m: float
    connectivity_score: float
    energy_kwh: float

    def __post_init__(self) -> None:
        if self.distance_km < 0 or self.travel_time_minutes < 0 or self.energy_kwh < 0:
            raise ValueError("distance, time, and energy must be non-negative")
        if not 0 <= self.connectivity_score <= 100:
            raise ValueError("connectivity_score must be between 0 and 100")


@dataclass(frozen=True)
class RouteScore:
    score: float
    predicted_offline_probability: float
    offline_prefetch_required: bool


def score_route(segments: list[RouteSegment], offline_threshold: float = 0.4) -> RouteScore:
    """Experimental, transparent heuristic—not a scientific routing model."""
    if not segments:
        raise ValueError("a route requires at least one segment")
    if not 0 <= offline_threshold <= 1:
        raise ValueError("offline_threshold must be between 0 and 1")
    total_distance = sum(segment.distance_km for segment in segments)
    weighted_connectivity = sum(
        segment.connectivity_score * segment.distance_km for segment in segments
    ) / (total_distance or len(segments))
    offline_probability = round(1 - weighted_connectivity / 100, 3)
    total_time = sum(segment.travel_time_minutes for segment in segments)
    total_energy = sum(segment.energy_kwh for segment in segments)
    elevation_penalty = sum(max(segment.elevation_change_m, 0) for segment in segments) / 100
    score = max(
        0,
        round(
            100
            - (offline_probability * 45)
            - min(total_time / 10, 20)
            - min(total_energy * 3, 20)
            - min(elevation_penalty, 15),
            2,
        ),
    )
    return RouteScore(score, offline_probability, offline_probability > offline_threshold)
