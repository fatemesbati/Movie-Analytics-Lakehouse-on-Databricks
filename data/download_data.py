"""Download and extract the MovieLens small dataset."""
import urllib.request
import zipfile
import os

URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
DATA_DIR = os.path.dirname(__file__)
ZIP_PATH = os.path.join(DATA_DIR, "ml-latest-small.zip")
EXTRACT_DIR = os.path.join(DATA_DIR, "raw")


def download():
    if os.path.exists(os.path.join(EXTRACT_DIR, "ml-latest-small")):
        print("Data already downloaded.")
        return
    print("Downloading MovieLens small dataset (~1 MB)...")
    urllib.request.urlretrieve(URL, ZIP_PATH)
    print("Extracting...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(EXTRACT_DIR)
    os.remove(ZIP_PATH)
    print(f"Done. Files are in: {EXTRACT_DIR}/ml-latest-small/")


if __name__ == "__main__":
    download()
