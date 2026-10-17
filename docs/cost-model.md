# Cost model

Parquet Silver and date predicates reduce Athena bytes scanned; queries should select columns rather than `*`. Glue is invoked on demand and should be monitored for runtime. S3 lifecycle moves Bronze after 30 days and expires it after one year; tune retention to actual needs. There are no continuously running compute resources in V1.

