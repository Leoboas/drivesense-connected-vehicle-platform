# AWS architecture

Terraform creates private S3 data and Athena-results buckets, versioning/lifecycle for Bronze, Glue catalog/crawler/job, and an Athena workgroup enforcing its output location. The Glue role is service-assumable and scoped to the project bucket for listing and object operations, plus the AWS managed Glue service policy. Credentials never enter source control.

QuickSight is deliberately manual: point datasets at validated Athena Gold views once an AWS account and QuickSight edition/permissions are available.

