output "raw_dataset_id" {
  description = "BigQuery dataset for raw (bronze) tables"
  value       = google_bigquery_dataset.raw.dataset_id
}

output "dbt_dev_dataset_id" {
  description = "BigQuery dataset for dbt dev output"
  value       = google_bigquery_dataset.dbt_dev.dataset_id
}

output "dbt_prod_dataset_id" {
  description = "BigQuery dataset for dbt prod output"
  value       = google_bigquery_dataset.dbt_prod.dataset_id
}

output "dbt_service_account_email" {
  description = "Service account email used by dbt"
  value       = google_service_account.dbt.email
}

output "loader_service_account_email" {
  description = "Service account email used by the data loader"
  value       = google_service_account.loader.email
}
