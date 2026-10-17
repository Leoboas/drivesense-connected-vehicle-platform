# Operational runbook

| Signal | Likely cause | Diagnosis | Recovery |
| --- | --- | --- | --- |
| Glue job failed | Contract/schema or IAM issue | Glue run logs; inspect job arguments and S3 paths | Correct scoped input/role; rerun a scoped backfill, never append blindly. |
| Athena query failed | Missing partition, incompatible view, or access issue | Query ID, workgroup output and catalog table | Fix view/table or partition; rerun with a date predicate. |
| S3 permission denied | Wrong role policy or bucket policy | IAM policy simulator/CloudTrail and exact ARN | Grant only the missing bucket/prefix action; retry on demand. |
| Quarantine spike | Producer regression or rule change | Group quarantine by `rule_id` and schema version | Stop promotion, remediate producer/rule, scoped reprocess. |
| Sync retry spike/backlog growth | Connectivity failure or sender outage | Buffer status counts and retry timestamps | Keep buffering, restore sender, reconcile in occurred-at order. |
| Duplicate spike | Producer retry bug | Compare attempted vs persisted IDs | Preserve Bronze, deduplicate by `event_id`, investigate producer. |
| Spark job slow/high shuffle | Skew, too many small files, unfiltered join | Spark UI stages, SQL plan, shuffle metrics | Filter/project early; check broadcast eligibility; tune partitions using recorded evidence. |

All recovery runs must include a correlation/job ID and record their scope, input path, output path, records written and quarantine count.
