"""Simple tests for the core MovieLens transformation functions."""
import os
import sys

import pytest
from pyspark.sql import SparkSession

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("movielens-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


def test_cast_ratings_converts_columns_to_useful_types(spark):
    from src.transformations import cast_ratings

    raw = spark.createDataFrame(
        [("1", "10", "4.5", "1000000000")],
        ["userId", "movieId", "rating", "timestamp"],
    )

    row = cast_ratings(raw).first()

    assert row is not None
    assert row["userId"] == 1
    assert row["movieId"] == 10
    assert row["rating"] == 4.5
    assert row["timestamp"] is not None


def test_drop_invalid_ratings_keeps_only_valid_rows(spark):
    from src.transformations import drop_invalid_ratings

    ratings = spark.createDataFrame(
        [
            (1, 10, 4.5),
            (2, 20, 0.0),
            (3, 30, 5.5),
            (None, 40, 3.0),
        ],
        ["userId", "movieId", "rating"],
    )

    result = drop_invalid_ratings(ratings).collect()

    assert len(result) == 1
    assert result[0]["userId"] == 1


def test_process_movies_extracts_release_year_and_cleans_title(spark):
    from src.transformations import process_movies

    movies = spark.createDataFrame(
        [("1", "Toy Story (1995)", "Animation|Children")],
        ["movieId", "title", "genres"],
    )

    row = process_movies(movies).first()

    assert row is not None
    assert row["movieId"] == 1
    assert row["title"] == "Toy Story"
    assert row["release_year"] == 1995


def test_split_genres_creates_one_row_per_genre(spark):
    from src.transformations import split_genres

    movies = spark.createDataFrame(
        [(1, "Toy Story", "Animation|Children")],
        ["movieId", "title", "genres"],
    )

    genres = {row["genre"] for row in split_genres(movies).collect()}

    assert genres == {"Animation", "Children"}


def test_top_movies_respects_minimum_rating_count(spark):
    from src.transformations import top_movies_by_ratings

    ratings = spark.createDataFrame(
        [(1, 4.0), (1, 5.0), (2, 3.0)],
        ["movieId", "rating"],
    )
    movies = spark.createDataFrame(
        [(1, "Popular Movie"), (2, "Less Rated Movie")],
        ["movieId", "title"],
    )

    result = top_movies_by_ratings(ratings, movies, min_ratings=2).collect()

    assert len(result) == 1
    assert result[0]["title"] == "Popular Movie"
