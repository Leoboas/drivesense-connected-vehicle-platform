output "data_bucket" { value = module.s3.data_bucket_id }
output "glue_database" { value = module.glue.database_name }
output "silver_table" { value = module.glue.silver_table_name }
output "athena_workgroup" { value = module.athena.workgroup_name }

