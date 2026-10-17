from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from drivesense.contracts.validation import validate_telemetry
from drivesense.quality.quarantine import quarantine_payload


@dataclass(frozen=True)
class BackfillScope:
    event_date: str | None = None
    vehicle_id: str | None = None
    trip_id: str | None = None

    def matches(self, payload: dict[str, Any]) -> bool:
        timestamp = payload.get("timestamp")
        return (
            (
                self.event_date is None
                or (isinstance(timestamp, str) and timestamp.startswith(self.event_date))
            )
            and (self.vehicle_id is None or payload.get("vehicle_id") == self.vehicle_id)
            and (self.trip_id is None or payload.get("trip_id") == self.trip_id)
        )


@dataclass(frozen=True)
class BackfillResult:
    scanned: int
    matched: int
    written: int
    duplicates: int
    quarantined: int
    dry_run: bool
    run_at: str


def reprocess_jsonl(
    source: Path,
    target: Path,
    scope: BackfillScope,
    *,
    quarantine_path: Path,
    force: bool = False,
    dry_run: bool = False,
) -> BackfillResult:
    """Build a deterministic scoped result; replacement prevents Gold duplication."""
    if target.exists() and not force and not dry_run:
        raise FileExistsError("target exists; use force to replace this scoped reprocessing result")
    scanned = matched = duplicates = quarantined = 0
    retained: dict[str, dict[str, Any]] = {}
    with source.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            scanned += 1
            payload: dict[str, Any] = json.loads(line)
            if not scope.matches(payload):
                continue
            matched += 1
            contract = validate_telemetry(payload)
            if not contract.accepted:
                quarantined += 1
                if not dry_run:
                    quarantine_payload(
                        quarantine_path, payload, ";".join(contract.errors), "DATA_CONTRACT"
                    )
                continue
            event_id = str(payload["event_id"])
            if event_id in retained:
                duplicates += 1
                continue
            retained[event_id] = payload
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary_target = target.with_suffix(f"{target.suffix}.tmp")
        with temporary_target.open("w", encoding="utf-8") as stream:
            for event_id in sorted(retained):
                stream.write(json.dumps(retained[event_id], sort_keys=True) + "\n")
        temporary_target.replace(target)
    return BackfillResult(
        scanned=scanned,
        matched=matched,
        written=len(retained),
        duplicates=duplicates,
        quarantined=quarantined,
        dry_run=dry_run,
        run_at=datetime.now(UTC).isoformat(),
    )
