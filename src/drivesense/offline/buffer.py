from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from drivesense.models import TelemetryEvent


class LocalEventBuffer:
    def __init__(self, database_path: Path) -> None:
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS buffered_events (
              event_id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL, occurred_at TEXT NOT NULL,
              payload TEXT NOT NULL, sync_status TEXT NOT NULL DEFAULT 'PENDING',
              retry_count INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL,
              last_attempt_at TEXT)"""
        )
        self.connection.commit()

    def enqueue(self, event: TelemetryEvent) -> bool:
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO buffered_events("
            "event_id,vehicle_id,occurred_at,payload,created_at) VALUES(?,?,?,?,?)",
            (
                event.event_id,
                event.vehicle_id,
                event.timestamp,
                json.dumps(event.to_dict()),
                datetime.now(UTC).isoformat(),
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def reconcile(self, sender: Callable[[TelemetryEvent], None]) -> tuple[int, int]:
        synced = failed = 0
        rows = self.connection.execute(
            "SELECT event_id,payload FROM buffered_events "
            "WHERE sync_status IN ('PENDING','FAILED') ORDER BY occurred_at"
        ).fetchall()
        for event_id, payload in rows:
            now = datetime.now(UTC).isoformat()
            self.connection.execute(
                "UPDATE buffered_events SET sync_status='SYNCING',"
                "last_attempt_at=? WHERE event_id=?",
                (now, event_id),
            )
            try:
                sender(TelemetryEvent(**json.loads(payload)))
                self.connection.execute(
                    "UPDATE buffered_events SET sync_status='SYNCED' WHERE event_id=?", (event_id,)
                )
                synced += 1
            except Exception:
                self.connection.execute(
                    "UPDATE buffered_events SET sync_status='FAILED',"
                    "retry_count=retry_count+1 WHERE event_id=?",
                    (event_id,),
                )
                failed += 1
            self.connection.commit()
        return synced, failed

    def close(self) -> None:
        self.connection.close()
