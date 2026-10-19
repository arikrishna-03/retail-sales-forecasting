"""Utility script to download the Walmart retail sales dataset.

Fetches the public benchmark CSV from a reliable public mirror and saves it
to data/raw/walmart_sales.csv.
"""

from pathlib import Path
import sys
import requests

DATASET_URL = (
    "https://raw.githubusercontent.com/DrPoojaAbhijith/"
    "Walmart-Sales-Forecasting/main/Walmart%20DataSet.csv"
)

EXPECTED_COLUMNS = [
    "Store",
    "Date",
    "Weekly_Sales",
    "Holiday_Flag",
    "Temperature",
    "Fuel_Price",
    "CPI",
    "Unemployment",
]


def download_dataset(force: bool = False) -> Path:
    """Downloads raw Walmart dataset into data/raw/walmart_sales.csv.

    Args:
        force (bool): If True, re-downloads even if the file exists.

    Returns:
        Path: Path to the downloaded file.
    """
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    destination = raw_dir / "walmart_sales.csv"

    if destination.exists() and not force:
        file_size_kb = destination.stat().st_size / 1024
        print(f"[INFO] Dataset already present at: {destination} ({file_size_kb:.1f} KB)")
        return destination

    print(f"[INFO] Downloading dataset from: {DATASET_URL}")
    try:
        response = requests.get(DATASET_URL, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[ERROR] Failed to download dataset: {exc}", file=sys.stderr)
        print(
            "[HINT] If you are offline, manually download the CSV and save it to:",
            destination,
            file=sys.stderr,
        )
        raise

    content = response.text
    # Basic validation
    header_line = content.splitlines()[0] if content else ""
    for col in EXPECTED_COLUMNS:
        if col not in header_line:
            raise ValueError(f"Downloaded file is missing expected column: {col}")

    destination.write_text(content, encoding="utf-8")
    file_size_kb = destination.stat().st_size / 1024
    print(f"[SUCCESS] Dataset saved to {destination} ({file_size_kb:.1f} KB)")
    return destination


if __name__ == "__main__":
    download_dataset()
