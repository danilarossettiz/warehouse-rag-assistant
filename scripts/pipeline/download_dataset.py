"""
Downloads the Olist Brazilian E-Commerce dataset from Kaggle
into the data/raw/ directory.

Requires Kaggle credentials configured at ~/.kaggle/kaggle.json
(Legacy API Key format). See project README for setup instructions.
"""

from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET = "olistbr/brazilian-ecommerce"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    api.authenticate()

    print(f"Downloading dataset '{DATASET}' to {OUTPUT_DIR} ...")
    api.dataset_download_files(DATASET, path=str(OUTPUT_DIR), unzip=True)
    print("Download complete.")


if __name__ == "__main__":
    main()
