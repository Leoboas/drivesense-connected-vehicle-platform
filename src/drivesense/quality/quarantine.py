from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QuarantineRecord:
    event_id: str | None
    failure_reason: str
    rule_id: str
    original_payload: dict[str, Any]
    ingestion_time: str


def quarantine_payload(
    output_path: Path, payload: dict[str, Any], failure_reason: str, rule_id: str
) -> QuarantineRecord:
    record = QuarantineRecord(
        event_id=payload.get("event_id") if isinstance(payload.get("event_id"), str) else None,
        failure_reason=failure_reason,
        rule_id=rule_id,
        original_payload=payload,
        ingestion_time=datetime.now(UTC).isoformat(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return record
