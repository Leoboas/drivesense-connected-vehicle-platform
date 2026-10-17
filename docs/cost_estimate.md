# Cost guardrails

This is a planning aid, not a price quote. Reference date: 2026-10-16; check current regional AWS pricing before any cloud execution.

- S3: keep raw demo datasets and Spark event logs in the data bucket; lifecycle transitions Bronze after 30 days and expires it after 365 days. Athena result artifacts expire after 30 days because they are reproducible.
- Glue: invoke manually only. Record actual DPU seconds and duration after the first run before projecting a demo cost.
- Athena: use Parquet, date predicates and selected columns. Record bytes scanned from each query execution; estimate cost using the current published regional/TB scan price rather than a hardcoded number.
- QuickSight: may incur recurring edition/user charges; it is BLOCKED_EXTERNAL until the account owner chooses to enable it.

No EC2, cluster, schedule, or continuously running compute is part of the V2 design.
