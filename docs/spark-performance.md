# Spark Performance Analysis

## Status

No real Spark/Glue execution has been performed yet, so this report deliberately contains no runtime, shuffle, stage, executor or DPU figures.

## Baseline plan

The first recorded baseline will read Bronze JSON, enforce the contract, deduplicate by `event_id`, calculate trip windows and write date-partitioned Silver Parquet. Record source records/bytes, output files, partitions, wall-clock duration, stage count, shuffle read/write and DPU seconds.

## Optimization hypotheses

Compare the baseline with projection/filter pushdown, built-in Spark expressions rather than Python UDFs, a broadcast vehicle-metadata join when its real size is safe, and deliberate repartition/coalesce settings. Keep only changes whose real run evidence improves a relevant metric; cache only reused datasets.

## Reproduction

Glue configuration enables continuous logs, metrics, Spark UI and S3 event logs under `spark-event-logs/`. The AWS execution gate must record links/exports from those artifacts in `docs/execution-results/`.
