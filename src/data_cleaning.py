"""Data Cleaning and Preparation Module for Retail Sales Forecasting.

Loads raw retail sales records, validates schema integrity, parses dates,
conducts outlier diagnostics, engineers calendar features, and exports clean
tabular data ready for modeling.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def get_project_root() -> Path:
    """Returns the absolute root directory of the project."""
    return Path(__file__).resolve().parent.parent


def load_raw_data(filepath: Path | str | None = None) -> pd.DataFrame:
    """Loads raw sales CSV from disk.

    Args:
        filepath: Optional path to raw dataset. Defaults to data/raw/walmart_sales.csv.

    Returns:
        pd.DataFrame: Raw dataset.
    """
    if filepath is None:
        filepath = get_project_root() / "data" / "raw" / "walmart_sales.csv"
    else:
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. Run `python src/download_data.py` first."
        )

    df = pd.read_csv(filepath)
    return df


def inspect_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Inspects structural integrity, missing values, duplicates, and ranges.

    Args:
        df: Input DataFrame.

    Returns:
        Dict[str, Any]: Inspection metrics dictionary.
    """
    inspection = {
        "num_rows": int(df.shape[0]),
        "num_columns": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "total_nulls": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_stores": int(df["Store"].nunique()) if "Store" in df.columns else None,
        "sales_summary": {
            "min": float(df["Weekly_Sales"].min()),
            "mean": float(df["Weekly_Sales"].mean()),
            "median": float(df["Weekly_Sales"].median()),
            "max": float(df["Weekly_Sales"].max()),
            "std": float(df["Weekly_Sales"].std()),
        }
        if "Weekly_Sales" in df.columns
        else {},
    }
    return inspection


def detect_outliers(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Analyzes statistical sales outliers using the 1.5 * IQR rule.

    Crucial Data Science Insight:
    In retail, sales surges during Thanksgiving (Black Friday) and pre-Christmas
    are real seasonal demand spikes, NOT recording errors. Capping or deleting
    them causes massive under-forecasting and costly out-of-stock events.

    Args:
        df: DataFrame containing Weekly_Sales.

    Returns:
        Tuple[pd.DataFrame, Dict[str, float]]: Outlier records and threshold metrics.
    """
    q1 = df["Weekly_Sales"].quantile(0.25)
    q3 = df["Weekly_Sales"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (df["Weekly_Sales"] < lower_bound) | (df["Weekly_Sales"] > upper_bound)
    outliers = df[outlier_mask].copy()

    metrics = {
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_count": int(outliers.shape[0]),
        "outlier_percentage": float(outliers.shape[0] / len(df) * 100),
    }
    return outliers, metrics


def clean_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans raw retail sales data and engineers calendar/temporal features.

    Transformations:
    1. Parse 'Date' from DD-MM-YYYY format into datetime64.
    2. Sort observations chronologically by Store and Date.
    3. Extract Year, Month, WeekOfYear, Quarter.
    4. Flag Pre-Christmas surge week (calendar week 51 / dates around Dec 17-24).
    5. Validate non-negativity of target sales.

    Args:
        df: Raw DataFrame.

    Returns:
        pd.DataFrame: Cleaned and feature-enriched DataFrame.
    """
    cleaned = df.copy()

    # 1. Date conversion (raw format is DD-MM-YYYY)
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], format="%d-%m-%Y")

    # 2. Sort chronologically per store to prevent temporal leakage
    cleaned = cleaned.sort_values(by=["Store", "Date"]).reset_index(drop=True)

    # 3. Calendar & Temporal Features
    cleaned["Year"] = cleaned["Date"].dt.year
    cleaned["Month"] = cleaned["Date"].dt.month
    cleaned["WeekOfYear"] = cleaned["Date"].dt.isocalendar().week.astype(int)
    cleaned["Day"] = cleaned["Date"].dt.day
    cleaned["Quarter"] = cleaned["Date"].dt.quarter

    # 4. Pre-Christmas shopping rush indicator
    # Retailers experience maximum pre-holiday footfall in week 51 right before Christmas
    cleaned["Is_PreChristmas"] = (
        (cleaned["Month"] == 12) & (cleaned["Day"].between(17, 24))
    ).astype(int)

    # 5. Quality validation
    if (cleaned["Weekly_Sales"] < 0).any():
        raise ValueError("Detected unexpected negative sales records in cleaned dataset.")

    return cleaned


def save_processed_data(df: pd.DataFrame, output_path: Path | str | None = None) -> Path:
    """Exports cleaned dataset to data/processed/clean_sales.csv.

    Args:
        df: Cleaned DataFrame.
        output_path: Optional destination path.

    Returns:
        Path: Destination path.
    """
    if output_path is None:
        output_path = get_project_root() / "data" / "processed" / "clean_sales.csv"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Cleaned data exported to: {output_path} ({df.shape[0]} rows, {df.shape[1]} cols)")
    return output_path


def run_pipeline() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Runs end-to-end data loading, inspection, cleaning, and storage pipeline."""
    raw_df = load_raw_data()
    inspection = inspect_data(raw_df)
    _, outlier_metrics = detect_outliers(raw_df)
    clean_df = clean_and_engineer_features(raw_df)
    save_processed_data(clean_df)
    return clean_df, {"inspection": inspection, "outliers": outlier_metrics}


if __name__ == "__main__":
    print("=" * 60)
    print("Starting Retail Sales Data Cleaning Pipeline")
    print("=" * 60)
    cleaned_df, report = run_pipeline()
    print("\nData Inspection Summary:")
    for k, v in report["inspection"].items():
        print(f"  - {k}: {v}")
    print("\nOutlier Diagnostics (1.5 * IQR):")
    for k, v in report["outliers"].items():
        print(f"  - {k}: {v}")
    print("\nCleaned Data Preview (first 3 rows):")
    print(cleaned_df.head(3))
