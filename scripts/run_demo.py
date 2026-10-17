from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from drivesense.analytics.hmi import hmi_metrics
from drivesense.offline.buffer import LocalEventBuffer
from drivesense.telemetry.generator import GeneratorConfig, generate_events


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the reproducible local DriveSense failure scenario."
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data/local/demo"))
    parser.add_argument("--events", type=int, default=100)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    events = generate_events(
        GeneratorConfig(
            vehicles=2,
            trips=2,
            events=args.events,
            offline_probability=1,
            warning_failure_probability=0.3,
            duplicate_probability=0.1,
            seed=7,
        )
    )
    buffer = LocalEventBuffer(args.output_dir / "edge-buffer.db")
    inserted = sum(buffer.enqueue(event) for event in events)
    first_synced, first_failed = buffer.reconcile(
        lambda _: (_ for _ in ()).throw(ConnectionError("simulated cellular outage"))
    )
    recovered: list[str] = []
    synced, failed = buffer.reconcile(lambda event: recovered.append(event.event_id))
    buffer.close()
    report = {
        "scenario": "connectivity-loss-hmi-warning",
        "events_attempted": len(events),
        "events_buffered": inserted,
        "duplicates_attempted": len(events) - len({event.event_id for event in events}),
        "first_sync": {"synced": first_synced, "failed": first_failed},
        "recovery": {"synced": synced, "failed": failed, "logical_events": len(set(recovered))},
        "hmi": asdict(hmi_metrics(events)),
    }
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
