from __future__ import annotations

import argparse
from pathlib import Path

from drivesense.reprocessing.backfill import BackfillScope, reprocess_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Scoped, idempotent DriveSense JSONL backfill.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--quarantine", type=Path, default=Path("data/local/quarantine.jsonl"))
    parser.add_argument("--date", dest="event_date")
    parser.add_argument("--vehicle-id")
    parser.add_argument("--trip-id")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = reprocess_jsonl(
        args.source,
        args.target,
        BackfillScope(args.event_date, args.vehicle_id, args.trip_id),
        quarantine_path=args.quarantine,
        force=args.force,
        dry_run=args.dry_run,
    )
    print(result)


if __name__ == "__main__":
    main()
