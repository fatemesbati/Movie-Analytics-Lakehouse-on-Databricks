"""Bronze layer — raw ingestion of MovieLens CSVs into Delta tables."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from src.transformations import add_ingestion_timestamp

builder = (
    SparkSession.builder
    .appName("MovieLens Bronze")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

RAW_PATH    = "/home/jovyan/work/data/raw/ml-latest-small"
BRONZE_PATH = "/home/jovyan/work/delta/bronze"

# ── ratings ───────────────────────────────────────────────────────────────────
raw_ratings = spark.read.option("header", "true").csv(f"{RAW_PATH}/ratings.csv")
print(f"Raw ratings: {raw_ratings.count():,} rows")
(
    add_ingestion_timestamp(raw_ratings)
    .write.format("delta").mode("overwrite").save(f"{BRONZE_PATH}/ratings")
)
print("bronze/ratings written.")

# ── movies ────────────────────────────────────────────────────────────────────
raw_movies = spark.read.option("header", "true").csv(f"{RAW_PATH}/movies.csv")
print(f"Raw movies: {raw_movies.count():,} rows")
(
    add_ingestion_timestamp(raw_movies)
    .write.format("delta").mode("overwrite").save(f"{BRONZE_PATH}/movies")
)
print("bronze/movies written.")

# ── tags ──────────────────────────────────────────────────────────────────────
raw_tags = spark.read.option("header", "true").csv(f"{RAW_PATH}/tags.csv")
print(f"Raw tags: {raw_tags.count():,} rows")
(
    add_ingestion_timestamp(raw_tags)
    .write.format("delta").mode("overwrite").save(f"{BRONZE_PATH}/tags")
)
print("bronze/tags written.")

print("\nBronze layer complete. All CSVs landed as Delta tables.")
spark.stop()
