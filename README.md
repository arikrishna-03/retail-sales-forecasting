# Retail Sales Forecasting and Inventory Planning Using Python

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: Educational Use](https://img.shields.io/badge/License-Non--Commercial%20Research-lightgrey.svg)](data/README.md)
[![Project Status: Week 2 Complete](https://img.shields.io/badge/Status-Week%202%20Verified-success.svg)](reports/figures/)

## 1. Project Overview
This repository contains the end-to-end data science implementation for the **YuvaIntern Virtual Data Science Explorer Internship** project: **Retail Sales Forecasting and Inventory Planning Using Python**.

The primary objective is to analyze historical weekly retail sales data across 45 stores, establish empirical demand trends and holiday surge behavior, construct robust predictive forecasting models, and formulate data-driven inventory replenishment policies (safety stock buffers and reorder points).

---

## 2. Internship Roadmap & Progress

| Phase / Week | Scope & Deliverables | Status | Deliverable Locations |
| :--- | :--- | :--- | :--- |
| **Week 1** | Project Planning, Problem Formulation & Timeline Definition | Completed | Submitted |
| **Week 2** | Data Retrieval, Cleaning, EDA, Statistical Audit & Figure Export | Completed & Verified | `src/`, `notebooks/`, `reports/figures/`, `reports/Week_2_EDA_and_Data_Preparation.docx` |
| **Week 3** | Baseline Forecasting & Chronological Validation Setup | Upcoming | `src/forecasting.py`, `notebooks/03_sales_forecasting.ipynb` |
| **Week 4** | Machine Learning Model Construction & Hyperparameter Tuning | Upcoming | `src/forecasting.py` |
| **Week 5** | Model Evaluation (MAE, RMSE, WMAPE) & Inventory Planning (ROP, Safety Stock) | Upcoming | `src/inventory.py` |
| **Week 6** | Executive Project Summary & Final Recommendation Report | Upcoming | `reports/Final_Project_Report.docx` |

---

## 3. Repository Architecture

```text
retail-sales-forecasting/
├── .gitignore                      # Excludes raw/processed data, checkpoints, and environment artifacts
├── requirements.txt                # Pinned production dependencies
├── README.md                       # Main project documentation
├── data/
│   ├── README.md                   # Dataset provenance, schema audit, and terms of use
│   ├── raw/
│   │   └── .gitkeep                # Untracked directory for raw data (walmart_sales.csv)
│   └── processed/
│       └── .gitkeep                # Untracked directory for cleaned data (clean_sales.csv)
├── notebooks/
│   ├── 01_data_inspection.ipynb    # Interactive schema audit, missing value checks & outlier diagnostics
│   ├── 02_exploratory_data_analysis.ipynb # Interactive visual trends, holiday uplift & correlation analysis
│   └── 03_sales_forecasting.ipynb  # (Upcoming) Predictive model development & evaluation
├── src/
│   ├── __init__.py                 # Python package initializer
│   ├── download_data.py            # Automated dataset retrieval utility with integrity checks
│   ├── data_cleaning.py            # Modular cleaning, date parsing & calendar feature engineering
│   ├── eda.py                      # Modular 300 DPI plotting pipeline and statistical reporting
│   ├── forecasting.py              # (Upcoming) Time-series baseline & machine learning regressors
│   └── inventory.py                # (Upcoming) Lead time, safety stock & reorder point calculators
├── reports/
│   ├── figures/                    # Publication-grade visualization figures (.png)
│   ├── Week_2_EDA_and_Data_Preparation.docx # Official Week 2 submission report
│   └── Week_2_Submission_Description.txt    # Text submission description for internship portal
└── scripts/
    └── build_notebooks.py          # Script to construct and validate project notebooks
```

---

## 4. Dataset & Provenance

* **Source Benchmark:** Kaggle *Walmart Recruiting - Store Sales Forecasting* (Walmart Inc., 2014).
* **Scope:** 45 unique retail store outlets observed across 143 contiguous weekly periods (February 5, 2010 to October 26, 2012), yielding 6,435 balanced observations.
* **Target Variable:** `Weekly_Sales` (Gross revenue per store per week in USD).
* **Features:** `Store`, `Date`, `Holiday_Flag`, `Temperature`, `Fuel_Price`, `CPI`, `Unemployment`.
* **Licensing Compliance:** Historical data is owned by Walmart Inc. and released under Kaggle Competition Rules for educational and academic research. Data files are excluded from Git version control to ensure compliance; an automated retrieval script is provided.

For full schema documentation and manual download instructions, refer to [data/README.md](data/README.md).

---

## 5. Verified Week 2 Empirical Findings

All reported findings have been empirically calculated and verified:

1. **Dataset Integrity:**
   * Rows: 6,435 | Columns: 8 raw, 14 engineered.
   * Missing Values: Exactly 0 across all fields.
   * Duplicate Records: 0.
   * Temporal Regularity: Exactly 143 weekly observations per store with zero gaps.
2. **Holiday Demand Uplift:**
   * Mean Non-Holiday Weekly Sales: **$1,041,256.38**
   * Mean Holiday Weekly Sales: **$1,122,887.89**
   * Average Demand Uplift: **+7.84%**
   * Statistical Significance: Confirmed via Welch's two-sample t-test ($t = 2.6801$, $p = 0.00760$) and non-parametric Mann-Whitney U test ($U = 1,431,297$, $p = 0.02589$).
3. **Outlier Diagnostics:**
   * 34 statistical outlier weeks identified above $Q_3 + 1.5 \times IQR$ ($>$ $2,720,371.49).
   * All 34 outliers occur during late November (Thanksgiving / Black Friday) or December (Christmas shopping rush). They are retained as genuine demand surges to prevent stockouts.
4. **Store Performance Variance:**
   * Top Store: **Store 20** ($301,397,792.46 total revenue; $2.11M weekly mean).
   * Lowest Store: **Store 33** ($37,160,221.96 total revenue; $260k weekly mean).
   * Disparity Ratio: **8.11×**, demonstrating the necessity of store-level demand segmentation.

---

## 6. Getting Started & Reproducibility

### 1. Clone the Repository
```bash
git clone https://github.com/arikrishna-03/retail-sales-forecasting.git
cd retail-sales-forecasting
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Fetch the Dataset
```bash
python src/download_data.py
```

### 4. Run the Data Cleaning Pipeline
```bash
python src/data_cleaning.py
```

### 5. Generate Visualizations & Statistical Reports
```bash
python src/eda.py
```
All visualization artifacts will be saved to `reports/figures/`.