from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from drivesense.models import TelemetryEvent


@dataclass(frozen=True)
class GeographyContext:
    scenario: str
    route_id: str
    route_segment: str
    region_type: str
    latitude: float
    longitude: float
    connection_state: str


SAO_PAULO_FLORIANOPOLIS_ROAD = (
    (-23.5505, -46.6333),  # São Paulo
    (-23.8090, -46.4050),  # acesso BR-116 / Baixada Santista
    (-24.4870, -47.8440),  # Registro
    (-25.4290, -49.2710),  # Curitiba
    (-26.3040, -48.8460),  # Joinville
    (-26.9100, -48.6700),  # Itajaí / BR-101
    (-27.5950, -48.5950),  # Florianópolis continental
    (-27.5954, -48.5480),  # acesso pela ponte, Florianópolis
)

FLORIANOPOLIS_LAND_TRAILS = {
    "LAGOA_DO_PERI": ((-27.7270, -48.5120), (-27.7380, -48.4980), (-27.7500, -48.5050)),
    "COSTAO_DA_LAGOA": ((-27.5900, -48.4610), (-27.6070, -48.4510), (-27.6230, -48.4580)),
    "MORRO_DA_LAGOA": ((-27.6030, -48.4820), (-27.6150, -48.4740), (-27.6290, -48.4810)),
}


def point_on_path(points: tuple[tuple[float, float], ...], progress: float) -> tuple[float, float]:
    """Interpolate a synthetic point on a declared road or trail corridor."""
    position = min(int(progress * (len(points) - 1)), len(points) - 2)
    segment_progress = progress * (len(points) - 1) - position
    start_latitude, start_longitude = points[position]
    end_latitude, end_longitude = points[position + 1]
    return (
        start_latitude + (end_latitude - start_latitude) * segment_progress,
        start_longitude + (end_longitude - start_longitude) * segment_progress,
    )


def road_segment(progress: float) -> str:
    return (
        "BR_116_SAO_PAULO_REGISTRO"
        if progress < 0.28
        else "BR_116_REGISTRO_CURITIBA"
        if progress < 0.48
        else "BR_101_CURITIBA_JOINVILLE"
        if progress < 0.68
        else "BR_101_JOINVILLE_ITAJAI"
        if progress < 0.88
        else "BR_101_FLORIANOPOLIS_ACCESS"
    )


def road_class_for(region_type: str) -> str:
    return {"URBAN": "URBAN_ARTERIAL", "HIGHWAY": "FEDERAL_HIGHWAY", "TRAIL": "UNPAVED_TRAIL"}[
        region_type
    ]


def geography_context(index: int, rng: random.Random) -> GeographyContext:
    """Return a synthetic Brazilian geography scenario for an event.

    Coordinates are illustrative route envelopes, never observations of real vehicles.
    """
    scenario_index = index % 4
    progress = ((index // 4) % 500) / 499
    if scenario_index == 0:
        return GeographyContext(
            "SAO_PAULO_URBAN",
            "sp-urban",
            rng.choice(["PAULISTA", "PINHEIROS", "MARGINAL_TIETE"]),
            "URBAN",
            -23.55 + rng.uniform(-0.045, 0.045),
            -46.63 + rng.uniform(-0.055, 0.055),
            "CONNECTED",
        )
    latitude, longitude = point_on_path(SAO_PAULO_FLORIANOPOLIS_ROAD, progress)
    if scenario_index == 1:
        return GeographyContext(
            "SAO_PAULO_FLORIANOPOLIS_CORRIDOR",
            "sp-florianopolis",
            road_segment(progress),
            "HIGHWAY",
            latitude + rng.uniform(-0.003, 0.003),
            longitude + rng.uniform(-0.003, 0.003),
            "DEGRADED" if rng.random() < 0.25 else "CONNECTED",
        )
    if scenario_index == 2:
        trail = rng.choice(["LAGOA_DO_PERI", "COSTAO_DA_LAGOA", "MORRO_DA_LAGOA"])
        trail_latitude, trail_longitude = point_on_path(
            FLORIANOPOLIS_LAND_TRAILS[trail], ((index // 4) % 100) / 99
        )
        return GeographyContext(
            "FLORIANOPOLIS_TRAILS",
            "florianopolis-trails",
            trail,
            "TRAIL",
            trail_latitude + rng.uniform(-0.001, 0.001),
            trail_longitude + rng.uniform(-0.001, 0.001),
            rng.choices(["CONNECTED", "DEGRADED", "OFFLINE"], weights=[35, 45, 20])[0],
        )
    variation_state = "CONNECTED" if progress < 0.20 or 0.55 <= progress < 0.75 else "DEGRADED"
    if 0.35 <= progress < 0.48:
        variation_state = "OFFLINE"
    return GeographyContext(
        "SP_FLORIANOPOLIS_CONNECTIVITY_VARIATION",
        "sp-florianopolis",
        road_segment(progress),
        "HIGHWAY",
        latitude + rng.uniform(-0.003, 0.003),
        longitude + rng.uniform(-0.003, 0.003),
        variation_state,
    )


@dataclass(frozen=True)
class GeneratorConfig:
    vehicles: int = 10
    trips: int = 20
    events: int = 1_000
    offline_probability: float = 0.05
    sensor_failure_probability: float = 0.01
    duplicate_probability: float = 0.02
    warning_failure_probability: float = 0.03
    network_instability: float = 0.1
    seed: int | None = 42

    def __post_init__(self) -> None:
        if self.vehicles < 1 or self.trips < 1 or self.events < 1:
            raise ValueError("vehicles, trips, and events must be positive")
        for name, value in self.__dict__.items():
            if name.endswith("probability") or name == "network_instability":
                if not 0 <= value <= 1:
                    raise ValueError(f"{name} must be between 0 and 1")


def generate_events(config: GeneratorConfig) -> list[TelemetryEvent]:
    rng = random.Random(config.seed)
    base = datetime(2026, 1, 1, tzinfo=UTC)
    output: list[TelemetryEvent] = []
    for index in range(config.events):
        vehicle_id = f"vehicle-{index % config.vehicles:04d}"
        trip_id = f"trip-{index % config.trips:05d}"
        geography = geography_context(index, rng)
        state = geography.connection_state
        if rng.random() < config.offline_probability:
            state = "OFFLINE"
        if state == "CONNECTED" and rng.random() < config.network_instability:
            state = "DEGRADED"
        speed_limit = 25 if geography.region_type == "TRAIL" else 120
        speed = round(rng.uniform(0, speed_limit), 2)
        battery = round(rng.uniform(15, 100), 2)
        if rng.random() < config.sensor_failure_probability:
            battery = 120.0
        detected = rng.random() < 0.12
        warning_time = None
        displayed_time = None
        if detected:
            warning_time = (base + timedelta(seconds=index, milliseconds=50)).isoformat()
            if rng.random() >= config.warning_failure_probability:
                displayed_time = (
                    base + timedelta(seconds=index, milliseconds=rng.randint(80, 600))
                ).isoformat()
        offline_duration = rng.randint(60, 900) if state == "OFFLINE" else 0
        reconnections = rng.randint(1, 5) if state in {"OFFLINE", "DEGRADED"} else 0
        sync_duration = rng.randint(500, 6000) if state == "OFFLINE" else 0
        packet_loss = (
            rng.uniform(15, 45)
            if state == "OFFLINE"
            else rng.uniform(3, 15)
            if state == "DEGRADED"
            else rng.uniform(0, 2)
        )
        buffered_bytes = rng.randint(100_000, 2_000_000) if state == "OFFLINE" else 0
        distance_remaining = round(max(0, 420 * (1 - ((index // 4) % 500) / 499)), 2)
        event_time = base + timedelta(seconds=index)
        warning_level = (
            "CRITICAL" if detected and rng.random() < 0.15 else "WARNING" if detected else "NONE"
        )
        event = TelemetryEvent(
            event_id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            trip_id=trip_id,
            timestamp=event_time.isoformat(),
            latitude=round(geography.latitude, 6),
            longitude=round(geography.longitude, 6),
            speed_kph=speed,
            battery_soc=battery,
            network_type="OFFLINE" if state == "OFFLINE" else rng.choice(["5G", "LTE", "3G"]),
            signal_dbm=round(rng.uniform(-120, -55), 1),
            latency_ms=round(rng.uniform(40, 1200 if state != "CONNECTED" else 150), 1),
            connection_state=state,
            proximity_front_cm=round(rng.uniform(5, 300), 1) if detected else None,
            object_detected=detected,
            warning_generated_at=warning_time,
            warning_displayed_at=displayed_time,
            scenario=geography.scenario,
            route_id=geography.route_id,
            route_segment=geography.route_segment,
            region_type=geography.region_type,
            offline_duration_s=offline_duration,
            reconnection_count=reconnections,
            sync_duration_ms=sync_duration,
            packet_loss_pct=round(packet_loss, 2),
            network_provider=rng.choice(["SYNTHETIC_PROVIDER_A", "SYNTHETIC_PROVIDER_B"]),
            bytes_buffered=buffered_bytes,
            road_class=road_class_for(geography.region_type),
            distance_remaining_km=distance_remaining,
            eta_minutes=round(distance_remaining / max(speed, 5) * 60, 1),
            reroute_count=rng.randint(0, 2) if state != "CONNECTED" else 0,
            map_match_confidence=round(
                rng.uniform(0.65, 0.9) if geography.region_type == "TRAIL" else rng.uniform(0.9, 1),
                2,
            ),
            screen_id=rng.choice(["NAVIGATION", "MEDIA", "VEHICLE_STATUS"]),
            interaction_type=rng.choice(["NONE", "TAP", "VOICE", "STEERING_WHEEL"]),
            warning_level=warning_level,
            driver_action="BRAKE"
            if warning_level == "CRITICAL"
            else "ACKNOWLEDGE"
            if detected
            else "NONE",
            driver_response_time_ms=rng.randint(300, 2500) if detected else None,
            battery_temperature_c=round(rng.uniform(18, 42), 1),
            energy_consumption_kwh=round(
                rng.uniform(0.05, 0.35) * (1.3 if geography.region_type == "HIGHWAY" else 1), 3
            ),
            range_estimate_km=round(battery * 3.8, 1),
            tire_pressure_status="LOW" if rng.random() < 0.02 else "NORMAL",
            vehicle_state="PARKED" if speed < 2 else "DRIVING",
            ingested_at=(event_time + timedelta(seconds=offline_duration)).isoformat(),
            late_arrival_seconds=offline_duration,
            retry_count=reconnections,
            processing_latency_ms=rng.randint(40, 500) + sync_duration,
            weather_condition=rng.choice(["CLEAR", "RAIN", "FOG"]),
            road_surface="WET" if rng.random() < 0.2 else "DRY",
            traffic_level=rng.choice(["LOW", "MODERATE", "HIGH"]),
            visibility_level="LOW" if rng.random() < 0.1 else "GOOD",
        )
        output.append(event)
        if rng.random() < config.duplicate_probability:
            output.append(event)
    rng.shuffle(output)  # deliberate out-of-order arrival simulation
    return output
