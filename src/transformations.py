"""Reusable PySpark transformation functions for the MovieLens lakehouse."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def add_ingestion_timestamp(df: DataFrame) -> DataFrame:
    return df.withColumn("ingestion_timestamp", F.current_timestamp())


def cast_ratings(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("userId",    F.col("userId").cast("integer"))
          .withColumn("movieId",   F.col("movieId").cast("integer"))
          .withColumn("rating",    F.col("rating").cast("double"))
          .withColumn("timestamp", F.to_timestamp(F.from_unixtime("timestamp")))
    )


def drop_invalid_ratings(df: DataFrame) -> DataFrame:
    return (
        df.dropna(subset=["userId", "movieId", "rating"])
          .filter(F.col("rating").between(0.5, 5.0))
    )


def deduplicate(df: DataFrame, key_cols: list[str]) -> DataFrame:
    return df.dropDuplicates(key_cols)


def process_movies(df: DataFrame) -> DataFrame:
    """Extract release year from title, clean title string, cast movieId."""
    return (
        df.withColumn("movieId", F.col("movieId").cast("integer"))
          .withColumn("release_year",
              F.when(
                  F.regexp_extract(F.col("title"), r"\((\d{4})\)$", 1) != "",
                  F.regexp_extract(F.col("title"), r"\((\d{4})\)$", 1).cast("integer")
              ))
          .withColumn("title",
              F.regexp_replace(F.col("title"), r"\s*\(\d{4}\)$", ""))
          .dropna(subset=["movieId", "title"])
          .dropDuplicates(["movieId"])
    )


def split_genres(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("genre", F.explode(F.split(F.col("genres"), r"\|")))
          .drop("genres")
          .filter(F.col("genre") != "(no genres listed)")
    )


def top_movies_by_ratings(ratings_df: DataFrame, movies_df: DataFrame, n: int = 20, min_ratings: int = 10) -> DataFrame:
    agg = (
        ratings_df.groupBy("movieId")
                  .agg(
                      F.count("*").alias("rating_count"),
                      F.round(F.avg("rating"), 2).alias("avg_rating"),
                  )
                  .filter(F.col("rating_count") >= min_ratings)
    )
    return (
        agg.join(movies_df.select("movieId", "title"), on="movieId", how="inner")
           .orderBy(F.desc("rating_count"))
           .limit(n)
           .select("title", "rating_count", "avg_rating")
    )


def avg_rating_by_genre(ratings_df: DataFrame, movies_with_genre_df: DataFrame) -> DataFrame:
    return (
        ratings_df.join(movies_with_genre_df, on="movieId", how="inner")
                  .groupBy("genre")
                  .agg(
                      F.round(F.avg("rating"), 2).alias("avg_rating"),
                      F.count("*").alias("total_ratings"),
                  )
                  .orderBy(F.desc("total_ratings"))
    )


def ratings_over_time(ratings_df: DataFrame) -> DataFrame:
    return (
        ratings_df.withColumn("year_month", F.date_format("timestamp", "yyyy-MM"))
                  .groupBy("year_month")
                  .agg(F.count("*").alias("rating_count"))
                  .orderBy("year_month")
    )


def user_activity_tiers(ratings_df: DataFrame) -> DataFrame:
    return (
        ratings_df.groupBy("userId")
                  .agg(
                      F.count("*").alias("ratings_given"),
                      F.round(F.avg("rating"), 2).alias("avg_rating_given"),
                  )
                  .withColumn("activity_tier",
                      F.when(F.col("ratings_given") >= 100, "power_user")
                       .when(F.col("ratings_given") >= 20,  "active")
                       .when(F.col("ratings_given") >= 5,   "casual")
                       .otherwise("one_time"))
    )
