"""Gold layer — business KPI tables with charts saved as PNG files."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from src.transformations import (
    top_movies_by_ratings,
    avg_rating_by_genre,
    ratings_over_time,
    user_activity_tiers,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

builder = (
    SparkSession.builder
    .appName("MovieLens Gold")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

SILVER_PATH = "/home/jovyan/work/delta/silver"
GOLD_PATH   = "/home/jovyan/work/delta/gold"
CHARTS_DIR  = "/home/jovyan/work/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

ratings  = spark.read.format("delta").load(f"{SILVER_PATH}/ratings")
movies   = spark.read.format("delta").load(f"{SILVER_PATH}/movies")
by_genre = spark.read.format("delta").load(f"{SILVER_PATH}/movies_by_genre")

# ── 1. Top 20 movies ──────────────────────────────────────────────────────────
gold_top_movies = top_movies_by_ratings(ratings, movies)
gold_top_movies.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/top_movies")
print("gold/top_movies written.")

top_pd = gold_top_movies.toPandas()
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(top_pd["title"][::-1], top_pd["rating_count"][::-1], color="steelblue")
ax.set_xlabel("Number of Ratings")
ax.set_title("Top 20 Most-Rated Movies")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/top_movies.png", dpi=100)
plt.close()
print("Chart saved: charts/top_movies.png")

# ── 2. Genre performance ──────────────────────────────────────────────────────
gold_genre = avg_rating_by_genre(ratings, by_genre)
gold_genre.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/genre_performance")
print("gold/genre_performance written.")

genre_pd = gold_genre.toPandas()
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(genre_pd["genre"][::-1], genre_pd["avg_rating"][::-1], color="darkorange")
ax.set_xlabel("Average Rating")
ax.set_title("Average Rating by Genre")
ax.set_xlim(0, 5)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/genre_performance.png", dpi=100)
plt.close()
print("Chart saved: charts/genre_performance.png")

# ── 3. Ratings over time ──────────────────────────────────────────────────────
gold_over_time = ratings_over_time(ratings)
gold_over_time.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/ratings_over_time")
print("gold/ratings_over_time written.")

time_pd = gold_over_time.toPandas()
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(range(len(time_pd)), time_pd["rating_count"], color="green", linewidth=1.5)
ax.set_xlabel("Year")
ax.set_ylabel("Ratings")
ax.set_title("Monthly Rating Activity")
year_ticks  = [i for i, ym in enumerate(time_pd["year_month"]) if ym.endswith("-01")]
year_labels = [ym[:4] for ym in time_pd["year_month"] if ym.endswith("-01")]
ax.set_xticks(year_ticks)
ax.set_xticklabels(year_labels, fontsize=10)
ax.grid(axis="x", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/ratings_over_time.png", dpi=100)
plt.close()
print("Chart saved: charts/ratings_over_time.png")

# ── 4. User activity tiers ────────────────────────────────────────────────────
gold_users = user_activity_tiers(ratings)
gold_users.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/user_activity")
print("gold/user_activity written.")

print("\nGold layer complete. Charts saved in charts/")
spark.stop()
