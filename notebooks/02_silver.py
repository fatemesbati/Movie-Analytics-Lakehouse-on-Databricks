"""Silver layer — clean, type-cast, deduplicate, and enrich bronze data."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from src.transformations import (
    cast_ratings,
    drop_invalid_ratings,
    deduplicate,
    process_movies,
    split_genres,
)

builder = (
    SparkSession.builder
    .appName("MovieLens Silver")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

BRONZE_PATH = "/home/jovyan/work/delta/bronze"
SILVER_PATH = "/home/jovyan/work/delta/silver"

# ── silver_ratings ────────────────────────────────────────────────────────────
bronze_ratings = spark.read.format("delta").load(f"{BRONZE_PATH}/ratings")

silver_ratings = deduplicate(
    drop_invalid_ratings(
        cast_ratings(bronze_ratings)
    ),
    key_cols=["userId", "movieId"]
).drop("ingestion_timestamp")

print(f"Bronze ratings: {bronze_ratings.count():,}")
print(f"Silver ratings: {silver_ratings.count():,}")
silver_ratings.write.format("delta").mode("overwrite").save(f"{SILVER_PATH}/ratings")
print("silver/ratings written.")

# ── silver_movies ─────────────────────────────────────────────────────────────
bronze_movies = spark.read.format("delta").load(f"{BRONZE_PATH}/movies")

silver_movies = process_movies(bronze_movies).drop("ingestion_timestamp")

print(f"Silver movies: {silver_movies.count():,}")
silver_movies.write.format("delta").mode("overwrite").save(f"{SILVER_PATH}/movies")
print("silver/movies written.")

# ── silver_movies_by_genre ────────────────────────────────────────────────────
silver_movies_by_genre = split_genres(silver_movies)

print(f"Silver movies by genre: {silver_movies_by_genre.count():,}")
silver_movies_by_genre.write.format("delta").mode("overwrite").save(f"{SILVER_PATH}/movies_by_genre")
print("silver/movies_by_genre written.")

# ── silver_ratings_enriched ───────────────────────────────────────────────────
silver_ratings_enriched = silver_ratings.join(
    silver_movies.select("movieId", "title", "release_year"),
    on="movieId", how="inner"
)

print(f"Silver ratings enriched: {silver_ratings_enriched.count():,}")
silver_ratings_enriched.write.format("delta").mode("overwrite").save(f"{SILVER_PATH}/ratings_enriched")
print("silver/ratings_enriched written.")

print("\nSilver layer complete.")
spark.stop()
