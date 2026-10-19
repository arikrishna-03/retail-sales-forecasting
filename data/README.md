# Dataset Documentation & Provenance: Walmart Store Sales

## 1. Overview & Business Context
This project utilizes the historical weekly sales dataset from 45 representative retail store outlets spanning from February 5, 2010 to October 26, 2012 (143 weeks per store, totaling 6,435 records). The dataset is utilized to evaluate store-level demand forecasting, assess holiday surge dynamics, and inform retail inventory planning (safety stock buffers and reorder schedules).

---

## 2. Provenance, Licensing & Terms of Use

* **Original Source:** Kaggle Competition — *Walmart Recruiting - Store Sales Forecasting* (Hosted by Walmart Inc., 2014).
* **Intellectual Property & Ownership:** The underlying transactional data is proprietary to Walmart Inc.
* **Competition Terms & Academic Usage:** Provided under Kaggle Competition Rules for educational benchmarking, machine learning research, and non-commercial academic evaluation. 
* **Redistribution Policy:** The dataset is **not** licensed under Creative Commons Zero (CC0) or Public Domain. Commercial redistribution is restricted under the original terms. 
* **Repository Compliance Strategy:** In alignment with open-source and data governance best practices, raw data files are **not committed to this GitHub repository** (enforced via `.gitignore`). Instead, an automated retrieval utility (`src/download_data.py`) and manual download instructions from public mirrors are provided for reproducibility.
* **Public Mirror Source:** `https://raw.githubusercontent.com/DrPoojaAbhijith/Walmart-Sales-Forecasting/main/Walmart%20DataSet.csv`

---

## 3. How to Obtain the Dataset

### Option A: Automated Download (Recommended)
Run the automated downloader from the project root:
```bash
python src/download_data.py
```
This fetches the dataset, verifies the file integrity (expected columns and minimum size), and saves it directly to `data/raw/walmart_sales.csv`.

### Option B: Manual Offline Download
If running in an offline environment or behind a corporate proxy:
1. Navigate in a browser to the mirror URL:
   `https://raw.githubusercontent.com/DrPoojaAbhijith/Walmart-Sales-Forecasting/main/Walmart%20DataSet.csv`
2. Save the raw text file as:
   `walmart_sales.csv`
3. Place the file inside your local clone at:
   `retail-sales-forecasting/data/raw/walmart_sales.csv`

---

## 4. Data Dictionary & Schema Audit

| Column Name | Raw Type | Target Type | Value Range / Units | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Store` | `int64` | `int64` | `1` to `45` | Unique categorical store identification index. |
| `Date` | `object` (`str`) | `datetime64[ns]` | `05-02-2010` to `26-10-2012` | End of sales week formatted as `DD-MM-YYYY`. |
| `Weekly_Sales` | `float64` | `float64` | `$209,986.25` to `$3,818,686.45` | Weekly gross sales revenue in USD (**Target Variable**). |
| `Holiday_Flag` | `int64` | `int64` | `0` or `1` | Binary flag indicating if the week contains a designated holiday. |
| `Temperature` | `float64` | `float64` | `-2.06°F` to `100.14°F` | Average ambient regional temperature in degrees Fahrenheit. |
| `Fuel_Price` | `float64` | `float64` | `$2.472` to `$4.468` | Prevailing regional retail fuel price per gallon in USD. |
| `CPI` | `float64` | `float64` | `126.06` to `227.23` | Regional Consumer Price Index (macroeconomic inflation index). |
| `Unemployment` | `float64` | `float64` | `3.879%` to `14.313%` | Prevailing regional unemployment rate as a percentage. |

### Calendar Holiday Schedule in Dataset:
The dataset marks four recurring annual promotional / holiday events (`Holiday_Flag = 1`):
1. **Super Bowl:** Week 6 of February (`2010-02-12`, `2011-02-11`, `2012-02-10`).
2. **Labor Day:** Week 36 of September (`2010-09-10`, `2011-09-09`, `2012-09-07`).
3. **Thanksgiving / Black Friday:** Week 47 of November (`2010-11-26`, `2011-11-25`).
4. **Christmas:** Final Friday of the year (`2010-12-31`, `2011-12-30`).

*Note on Pre-Christmas Rush:* The week immediately preceding Christmas Day (e.g., `2010-12-24` and `2011-12-23`) captures the heaviest retail purchasing surge of the year, although coded as `Holiday_Flag = 0`. Our pipeline accounts for this via an engineered `Is_PreChristmas` feature.

---

## 5. Dataset Limitations

1. **Store-Level Aggregation:** Data is aggregated weekly at the store level. Individual department-level, aisle-level, or SKU-level (barcode) granularities are not present in this consolidated table. Inventory recommendations apply at the aggregate replenishment buffer level.
2. **Temporal Span:** The 143-week duration (2.75 years) provides two complete annual cycles. While adequate for seasonal decomposition and 4-to-12-week horizon forecasting, it does not capture multi-year macroeconomic cycles.
3. **Environmental Feature Lag:** Regional CPI and Unemployment figures represent monthly macro series interpolated across weeks, exhibiting low high-frequency weekly variation.
