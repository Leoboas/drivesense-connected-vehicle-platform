# Offline-first recovery

| State | Behavior |
| --- | --- |
| CONNECTED | Send to cloud; buffer may be used for resilience. |
| DEGRADED | Persist before partial/retried send. |
| OFFLINE | Persist durable SQLite record as `PENDING`. |
| RECOVERY | Reconcile chronological pending/failed records; mark `SYNCED` only after sender success. |

Buffer statuses are `PENDING`, `SYNCING`, `SYNCED`, and `FAILED`. A failed send increments `retry_count`. Primary-key `event_id` prevents repeated buffering; downstream Glue deduplicates again for defense in depth.

