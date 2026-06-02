"""
Load raw MovieLens CSV files into BigQuery (movielens_raw dataset).
Run this once after `terraform apply` and before `dbt run`.

Usage:
    export GCP_PROJECT_ID=your-project-id
    export GOOGLE_APPLICATION_CREDENTIALS=secrets/loader-service-account.json
    python scripts/load_to_bigquery.py
"""

import os
import sys
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
if not PROJECT_ID:
    sys.exit("GCP_PROJECT_ID environment variable is not set.")

DATASET_ID = "movielens_raw"
DATA_DIR = Path(__file__).parent.parent / "data" / "raw" / "ml-latest-small"

TABLES = {
    "ratings": DATA_DIR / "ratings.csv",
    "movies":  DATA_DIR / "movies.csv",
    "tags":    DATA_DIR / "tags.csv",
}

client = bigquery.Client(project=PROJECT_ID)


def load_table(table_name: str, csv_path: Path) -> None:
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}  —  run `python data/download_data.py` first.")

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    df = pd.read_csv(csv_path, dtype=str)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"  {table_name}: {len(df):,} rows → {table_id}")


if __name__ == "__main__":
    print(f"Loading MovieLens data into {PROJECT_ID}.{DATASET_ID} ...\n")
    for name, path in TABLES.items():
        load_table(name, path)
    print("\nDone. Run `dbt run` next.")
