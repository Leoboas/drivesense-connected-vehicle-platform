# Cloud execution plan

## Region

Project selected Region: `us-east-2`, passed explicitly through `aws_region`. The final region must be recorded in the run manifest. Do not create project Regional resources in another Region.

## Resources and cost model

| Resource | Billing model | Idle cost | Execution cost | Cleanup required |
| --- | --- | --- | --- | --- |
| S3 data bucket | storage/request | low | storage + requests | Remove demo run prefixes when evidence is retained elsewhere. |
| S3 Athena results bucket | storage/request | low | query result storage | 30-day lifecycle covers temporary results. |
| Glue catalog/crawler | metadata/on-demand | near zero | crawler/job usage | No compute remains after run. |
| Glue Spark job | on-demand DPU time | zero | DPU duration | Job terminates; remove old event-log prefixes. |
| Athena workgroup | on-demand scan | zero | bytes scanned | Keep workgroup; expire temporary results. |
| CloudWatch/Glue logs | ingestion/storage | low | log ingestion/storage | Retain only evidence required by the portfolio. |

## Initial controlled run

Use a `DEMO_SMALL` profile: 1,000,000 generated events, fixed seed, 100 vehicles and 500 trips. It is the smallest intended cloud profile that should create meaningful partitions, joins and shuffle. The job is pinned to two `G.1X` workers; do not run `DEMO_MEDIUM` or benchmark scale until baseline evidence justifies it.

Use the current `us-east-2` pricing when making any estimate. Treat all planning ranges as non-binding: the first execution must record actual DPU seconds and query bytes scanned, and AWS Billing data can take time to appear.

## Commands

```bash
terraform -chdir=infra/terraform/environments/dev fmt -check -recursive
terraform -chdir=infra/terraform/environments/dev validate
python scripts/aws_preflight.py --region us-east-2
terraform -chdir=infra/terraform/environments/dev plan -var="aws_region=us-east-2" -out=tfplan
terraform show -no-color tfplan > docs/evidence/terraform-plan.txt
# After explicit approval only:
# terraform -chdir=infra/terraform/environments/dev apply tfplan
```

The later cloud-demo command must use a unique run ID and prefixes: `bronze/<run_id>/`, `silver/<run_id>/`, `gold/<run_id>/`, `spark-events/<run_id>/`, and `athena-results/<run_id>/`.

## Rollback and cleanup

Do not run `terraform destroy` automatically. Remove only the named demo prefixes after downloading evidence, then optionally destroy the isolated dev stack with human approval. Verify no unrelated S3 prefixes remain before deletion.

## External gate

`BLOCKED_EXTERNAL: AWS_EXECUTION_APPROVAL` — deployment, Glue execution and Athena queries require the account owner to approve cost and provide an authenticated AWS profile/region.
