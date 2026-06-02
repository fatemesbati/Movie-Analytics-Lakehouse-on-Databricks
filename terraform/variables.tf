variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "credentials_file" {
  description = "Path to the GCP service account JSON key used by Terraform itself"
  type        = string
  default     = "~/.config/gcloud/application_default_credentials.json"
}
