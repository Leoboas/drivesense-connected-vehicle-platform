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
    latitude = -23.55 + (-27.59 + 23.55) * progress
    longitude = -46.63 + (-48.55 + 46.63) * progress
    if scenario_index == 1:
        return GeographyContext(
            "SAO_PAULO_FLORIANOPOLIS_CORRIDOR",
            "sp-florianopolis",
            rng.choice(["SAO_PAULO_EXIT", "CURITIBA", "JOINVILLE", "FLORIANOPOLIS_ENTRY"]),
            "HIGHWAY",
            latitude + rng.uniform(-0.025, 0.025),
            longitude + rng.uniform(-0.025, 0.025),
            "DEGRADED" if rng.random() < 0.25 else "CONNECTED",
        )
    if scenario_index == 2:
        trail = rng.choice(["LAGOA_DO_PERI", "COSTAO_DA_LAGOA", "MORRO_DA_LAGOA"])
        return GeographyContext(
            "FLORIANOPOLIS_TRAILS",
            "florianopolis-trails",
            trail,
            "TRAIL",
            -27.62 + rng.uniform(-0.08, 0.08),
            -48.50 + rng.uniform(-0.08, 0.08),
            rng.choices(["CONNECTED", "DEGRADED", "OFFLINE"], weights=[35, 45, 20])[0],
        )
    variation_state = "CONNECTED" if progress < 0.20 or 0.55 <= progress < 0.75 else "DEGRADED"
    if 0.35 <= progress < 0.48:
        variation_state = "OFFLINE"
    return GeographyContext(
        "SP_FLORIANOPOLIS_CONNECTIVITY_VARIATION",
        "sp-florianopolis",
        "SERRA_DO_MAR" if progress < 0.48 else "VALE_DO_ITAJAI",
        "HIGHWAY",
        latitude + rng.uniform(-0.018, 0.018),
        longitude + rng.uniform(-0.018, 0.018),
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
        event = TelemetryEvent(
            event_id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            trip_id=trip_id,
            timestamp=(base + timedelta(seconds=index)).isoformat(),
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
            offline_duration_s=rng.randint(60, 900) if state == "OFFLINE" else 0,
            reconnection_count=rng.randint(1, 5) if state in {"OFFLINE", "DEGRADED"} else 0,
            sync_duration_ms=rng.randint(500, 6000) if state == "OFFLINE" else 0,
        )
        output.append(event)
        if rng.random() < config.duplicate_probability:
            output.append(event)
    rng.shuffle(output)  # deliberate out-of-order arrival simulation
    return output
