"""Validate the Delta outputs produced by the MovieLens lakehouse pipeline."""
import os

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


builder = (
    SparkSession.builder
    .appName("MovieLens Validation")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

BASE_PATH = "/home/jovyan/work"
BRONZE_PATH = f"{BASE_PATH}/delta/bronze"
SILVER_PATH = f"{BASE_PATH}/delta/silver"
GOLD_PATH = f"{BASE_PATH}/delta/gold"
CHARTS_DIR = f"{BASE_PATH}/charts"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def read_delta(path: str):
    return spark.read.format("delta").load(path)


bronze_ratings = read_delta(f"{BRONZE_PATH}/ratings")
silver_ratings = read_delta(f"{SILVER_PATH}/ratings")
silver_movies = read_delta(f"{SILVER_PATH}/movies")
gold_top_movies = read_delta(f"{GOLD_PATH}/top_movies")
gold_genre = read_delta(f"{GOLD_PATH}/genre_performance")
gold_over_time = read_delta(f"{GOLD_PATH}/ratings_over_time")
gold_users = read_delta(f"{GOLD_PATH}/user_activity")

bronze_count = bronze_ratings.count()
silver_count = silver_ratings.count()

print("\nRow counts")
print(f"bronze/ratings: {bronze_count:,}")
print(f"silver/ratings: {silver_count:,}")
print(f"silver/movies:  {silver_movies.count():,}")

assert_true(bronze_count > 0, "bronze ratings table is not empty")
assert_true(silver_count > 0, "silver ratings table is not empty")
assert_true(silver_count <= bronze_count, "silver ratings count does not exceed bronze")

invalid_ratings = silver_ratings.filter(
    F.col("userId").isNull()
    | F.col("movieId").isNull()
    | F.col("rating").isNull()
    | ~F.col("rating").between(0.5, 5.0)
).count()
assert_true(invalid_ratings == 0, "silver ratings have no null or out-of-range records")

duplicate_ratings = (
    silver_ratings.groupBy("userId", "movieId")
    .count()
    .filter(F.col("count") > 1)
    .count()
)
assert_true(duplicate_ratings == 0, "silver ratings are deduplicated by userId and movieId")

missing_movie_ids = silver_movies.filter(F.col("movieId").isNull()).count()
assert_true(missing_movie_ids == 0, "silver movies have valid movie IDs")

assert_true(gold_top_movies.count() > 0, "gold/top_movies is populated")
assert_true(gold_genre.count() > 0, "gold/genre_performance is populated")
assert_true(gold_over_time.count() > 0, "gold/ratings_over_time is populated")
assert_true(gold_users.count() > 0, "gold/user_activity is populated")

low_rating_count_movies = gold_top_movies.filter(F.col("rating_count") < 10).count()
assert_true(low_rating_count_movies == 0, "top movies respect the minimum rating threshold")

expected_charts = [
    "top_movies.png",
    "genre_performance.png",
    "ratings_over_time.png",
]
for chart in expected_charts:
    chart_path = os.path.join(CHARTS_DIR, chart)
    assert_true(os.path.exists(chart_path), f"{chart} exists")
    assert_true(os.path.getsize(chart_path) > 0, f"{chart} is not empty")

print("\nValidation complete. Pipeline outputs look consistent.")
spark.stop()
