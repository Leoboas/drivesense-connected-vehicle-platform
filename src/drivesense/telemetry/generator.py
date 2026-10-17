from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from drivesense.models import TelemetryEvent


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
        state = "OFFLINE" if rng.random() < config.offline_probability else "CONNECTED"
        if state == "CONNECTED" and rng.random() < config.network_instability:
            state = "DEGRADED"
        speed = round(rng.uniform(0, 120), 2)
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
            latitude=round(-23.55 + rng.uniform(-0.05, 0.05), 6),
            longitude=round(-46.63 + rng.uniform(-0.05, 0.05), 6),
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
        )
        output.append(event)
        if rng.random() < config.duplicate_probability:
            output.append(event)
    rng.shuffle(output)  # deliberate out-of-order arrival simulation
    return output
