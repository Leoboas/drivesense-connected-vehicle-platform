# Backfill and controlled reprocessing

`scripts/backfill.py` reads immutable JSONL input, scopes by event date, vehicle and/or trip, validates contracts, deduplicates by `event_id`, and atomically replaces a scoped result only with `--force`. This prevents reruns from appending duplicate logical facts. `--dry-run` reports the affected records without changing a target or quarantine.

Example:

```bash
python scripts/backfill.py --source data/bronze/events.jsonl --target data/gold/2026-01-01.jsonl --date 2026-01-01 --force
```

Silver is source-preserving; the local V2 reprocessing output models a controlled Gold replacement. In AWS, the same scope must be passed to Glue and a versioned/prefix-replacement strategy used instead of an unbounded append.
