# MovieLens Lakehouse

A Databricks-style data engineering project built with PySpark, Delta Lake, Docker, and pytest.

I built this project to show that I understand the core workflow of a modern data pipeline: ingest raw data, clean and model it into trusted tables, publish business-ready KPIs, and validate that the output is correct.

The dataset is MovieLens Small, which contains 100k+ movie ratings. I used it like a small streaming/product analytics case study: top content, genre performance, rating trends, and user activity.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![PySpark](https://img.shields.io/badge/PySpark-4.1-orange?logo=apachespark)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-4.2-blue)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![Tests](https://img.shields.io/badge/Tests-pytest-green?logo=pytest)

---

## What This Project Demonstrates

- Building a medallion architecture with Bronze, Silver, and Gold layers
- Using PySpark for data cleaning, type casting, joins, aggregations, and KPI generation
- Writing Delta tables instead of loose CSV/Parquet outputs
- Separating reusable transformation logic into `src/transformations.py`
- Adding simple tests for important transformation rules
- Adding a validation script that checks the produced Delta tables and chart outputs
- Packaging the environment with Docker so the project can be run reproducibly

---

## Architecture

```text
Raw CSV files
  -> Bronze Delta tables
      -> Silver Delta tables
          -> Gold Delta KPI tables
              -> PNG charts
              -> validation checks
```

| Layer | Purpose | Examples |
|---|---|---|
| Bronze | Raw landing zone with ingestion timestamp | `bronze/ratings`, `bronze/movies`, `bronze/tags` |
| Silver | Clean, typed, deduplicated, enriched data | `silver/ratings`, `silver/movies`, `silver/movies_by_genre` |
| Gold | Business-ready KPI tables | `gold/top_movies`, `gold/genre_performance`, `gold/ratings_over_time`, `gold/user_activity` |

---

## Pipeline Steps

| Step | File | What it does |
|---|---|---|
| 1 | `notebooks/01_bronze.py` | Reads raw MovieLens CSV files and writes raw Delta tables |
| 2 | `notebooks/02_silver.py` | Casts types, removes invalid ratings, deduplicates records, extracts movie years, splits genres |
| 3 | `notebooks/03_gold.py` | Builds KPI tables and saves charts |
| 4 | `notebooks/04_validate.py` | Checks row counts, data quality rules, Gold tables, and chart files |

---

## Gold KPIs

| Table | Description |
|---|---|
| `gold/top_movies` | Top 20 most-rated movies with average rating |
| `gold/genre_performance` | Average rating and total ratings per genre |
| `gold/ratings_over_time` | Monthly rating activity for trend analysis |
| `gold/user_activity` | Users segmented by rating volume |

---

## Sample Outputs

### Top 20 Most-Rated Movies

![Top Movies](charts/top_movies.png)

### Average Rating by Genre

![Genre Performance](charts/genre_performance.png)

### Monthly Rating Activity

![Ratings Over Time](charts/ratings_over_time.png)

---

## How I Know The Results Are Correct

This project has two levels of checks.

### 1. Unit tests for transformation logic

The pytest suite checks the most important transformation rules:

- Ratings are cast into useful numeric/timestamp types
- Invalid ratings are removed
- Movie release years are extracted from titles
- Genre strings are split into one row per genre
- Top-movie logic respects the minimum rating threshold

Run:

```bash
python -m pytest tests/ -v
```

### 2. End-to-end validation after the pipeline runs

`notebooks/04_validate.py` reads the generated Delta tables and checks that:

- Bronze and Silver tables are populated
- Silver row count does not exceed Bronze row count
- Silver ratings have no null IDs, null ratings, or out-of-range ratings
- Silver ratings are deduplicated by `userId` and `movieId`
- Gold KPI tables are populated
- Top movies respect the minimum rating threshold
- Generated chart files exist and are not empty

Run after the pipeline:

```bash
python3 work/notebooks/04_validate.py
```

This gives concrete evidence that the pipeline output is internally consistent, not just visually plausible.

---

## How To Run

### Prerequisites

- Docker Desktop installed and running

### 1. Clone the repository and download the data

```bash
git clone https://github.com/fatemesbati/Movie-Analytics-Lakehouse-on-Databricks.git
cd Movie-Analytics-Lakehouse-on-Databricks
python data/download_data.py
```

### 2. Start JupyterLab

```bash
docker compose up --build
```

Open JupyterLab at:

```text
http://localhost:8080
```

### 3. Run the full pipeline inside the JupyterLab terminal

```bash
python3 work/notebooks/01_bronze.py
python3 work/notebooks/02_silver.py
python3 work/notebooks/03_gold.py
python3 work/notebooks/04_validate.py
```

Charts are saved to `charts/`.

---

## Project Structure

```text
movielens-lakehouse/
|-- data/
|   `-- download_data.py
|-- notebooks/
|   |-- 01_bronze.py
|   |-- 02_silver.py
|   |-- 03_gold.py
|   `-- 04_validate.py
|-- src/
|   `-- transformations.py
|-- tests/
|   `-- test_transformations.py
|-- charts/
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

---

## What I Learned

### Why separate Bronze, Silver, and Gold

Bronze preserves the raw input. Silver applies data quality and modeling rules. Gold answers business questions. This separation makes the pipeline easier to debug and rerun.

### Why Delta Lake

Delta Lake gives the project table-like behavior on top of files: ACID transactions, schema handling, and a more realistic lakehouse workflow than writing plain CSV files.

### Why validation matters

Charts alone do not prove a pipeline is correct. The validation step checks the actual Delta outputs and confirms that the key data quality assumptions still hold after the pipeline runs.

---

## Next Improvements

- Add GitHub Actions to run tests on every push
- Add Great Expectations or custom data quality reports
- Register the tables in Unity Catalog in a real Databricks workspace
- Replace batch CSV ingestion with Auto Loader
- Build a small Streamlit dashboard on top of the Gold tables

---

## Dataset

[MovieLens Small](https://grouplens.org/datasets/movielens/latest/) - F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM TiiS 5(4):19.
