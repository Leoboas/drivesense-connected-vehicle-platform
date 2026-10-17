# ADR-003: Use Parquet for Silver

**Decision:** write deduplicated Silver events as Parquet partitioned by event date. This reduces Athena scan costs and suits the expected analytical workload. Raw JSON remains Bronze for replay and debugging.

