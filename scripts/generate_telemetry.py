from __future__ import annotations

import argparse
import json
from pathlib import Path

from drivesense.telemetry.generator import GeneratorConfig, generate_events


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic DriveSense telemetry as JSONL."
    )
    for option in ("vehicles", "trips", "events"):
        parser.add_argument(f"--{option}", type=int, required=True)
    parser.add_argument("--offline-probability", type=float, default=0.05)
    parser.add_argument("--sensor-failure-probability", type=float, default=0.01)
    parser.add_argument("--duplicate-probability", type=float, default=0.02)
    parser.add_argument("--warning-failure-probability", type=float, default=0.03)
    parser.add_argument("--network-instability", type=float, default=0.1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = GeneratorConfig(**{key: value for key, value in vars(args).items() if key != "output"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for event in generate_events(config):
            stream.write(json.dumps(event.to_dict()) + "\n")


if __name__ == "__main__":
    main()
