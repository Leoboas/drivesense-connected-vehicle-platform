# ADR-004: Use Glue and PySpark for cloud transformation

**Decision:** use a Glue PySpark job for schema enforcement, quality flags, deduplication and enrichment. It satisfies the target AWS stack while preserving a locally testable Python domain layer.

