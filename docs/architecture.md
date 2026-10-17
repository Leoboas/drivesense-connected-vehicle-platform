# V1 architecture

The edge simulator emits immutable events. In CONNECTED state a sender may upload immediately; DEGRADED and OFFLINE states first persist events to SQLite. RECOVERY reconciles pending events in occurred-at order. SQLite enforces one row per `event_id`, which makes local retries idempotent. S3 Bronze retains raw JSON; Glue writes deduplicated, validated Parquet to Silver, and Athena views expose Gold models.

The initial partition key is `event_date`, matching daily fleet and quality queries while avoiding excessive small partitions by vehicle. Bronze is arranged by `year/month/day` when uploaded.

