# Project backlog

| ID | Priority | Component | Risk | Task | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DS-001 | P0 | Foundation | Regressions | Python, Docker, CI, tests and Git baseline | CI configuration | DONE |
| DS-002 | P0 | Telemetry | Bad synthetic coverage | Failure-injecting generator | Generator tests | DONE |
| DS-003 | P0 | Offline | Logical duplicate data | Durable buffer and reconciliation | Buffer tests | DONE |
| DS-004 | P0 | Quality | Invalid analytical facts | Validation rules and score | Quality tests | DONE |
| DS-009 | P0 | Contracts | Silent schema/data corruption | Versioned contracts and immutable quarantine | Contract tests | DONE |
| DS-010 | P1 | Reprocessing | Unrecoverable bad history | Scoped idempotent backfill and reprocessing | Backfill tests | DONE |
| DS-011 | P1 | Scenarios | Unproven recovery behavior | Reproducible connectivity/HMI demo | Scenario and HMI tests | DONE |
| DS-012 | P2 | Observability | Silent pipeline failure | Structured local metrics and runbook | Pending | TODO |
| DS-013 | P2 | Spark | Unmeasured distributed performance | Baseline and optimized Spark workloads | Pending | TODO |
| DS-005 | P1 | AWS | Unplanned cloud spend | Review Terraform plan with target AWS account | Terraform validate | BLOCKED_EXTERNAL |
| DS-006 | P1 | Analytics | Unverified cloud integration | Execute Glue and validate Athena/QuickSight datasets | None yet | BLOCKED_EXTERNAL |

