# ── BigQuery datasets ──────────────────────────────────────────────────────────

resource "google_bigquery_dataset" "raw" {
  dataset_id  = "movielens_raw"
  description = "Bronze layer: raw MovieLens CSV data loaded by the PySpark/loader script"
  location    = var.region
}

resource "google_bigquery_dataset" "dbt_dev" {
  dataset_id  = "movielens_dbt"
  description = "Silver + Gold layers produced by dbt (dev target)"
  location    = var.region
}

resource "google_bigquery_dataset" "dbt_prod" {
  dataset_id  = "movielens_dbt_prod"
  description = "Silver + Gold layers produced by dbt (prod target)"
  location    = var.region
}

# ── Service account for dbt ────────────────────────────────────────────────────

resource "google_service_account" "dbt" {
  account_id   = "movielens-dbt"
  display_name = "MovieLens dbt runner"
}

resource "google_project_iam_member" "dbt_bq_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_project_iam_member" "dbt_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_bigquery_dataset_iam_member" "dbt_raw_reader" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_bigquery_dataset_iam_member" "dbt_dev_editor" {
  dataset_id = google_bigquery_dataset.dbt_dev.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_bigquery_dataset_iam_member" "dbt_prod_editor" {
  dataset_id = google_bigquery_dataset.dbt_prod.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_service_account_key" "dbt_key" {
  service_account_id = google_service_account.dbt.name
}

resource "local_file" "dbt_key_file" {
  content         = base64decode(google_service_account_key.dbt_key.private_key)
  filename        = "${path.module}/../secrets/dbt-service-account.json"
  file_permission = "0600"
}

# ── Service account for the BigQuery loader script ─────────────────────────────

resource "google_service_account" "loader" {
  account_id   = "movielens-loader"
  display_name = "MovieLens BigQuery data loader"
}

resource "google_bigquery_dataset_iam_member" "loader_raw_editor" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.loader.email}"
}

resource "google_project_iam_member" "loader_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.loader.email}"
}

resource "google_service_account_key" "loader_key" {
  service_account_id = google_service_account.loader.name
}

resource "local_file" "loader_key_file" {
  content         = base64decode(google_service_account_key.loader_key.private_key)
  filename        = "${path.module}/../secrets/loader-service-account.json"
  file_permission = "0600"
}
