# Financial Performance Intelligence Dashboard

An end-to-end Finance Data Analyst portfolio project for **Meridian Industrial Systems**, a fictional B2B manufacturer. It combines reproducible synthetic financial data, Python analytics, PostgreSQL queries, teaching notebooks, automated tests, and a Streamlit dashboard.

[![Deploy on Streamlit Community Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Open%20App-FF4B4B?logo=streamlit&logoColor=white)](https://finance-data-analyst-project-041.streamlit.app/)

## 🚀 Live Dashboard

**[Open the live Financial Performance Intelligence Dashboard →](https://finance-data-analyst-project-041.streamlit.app/)**

> **Data disclosure:** every dataset is synthetic. It is not a public-company filing, audited information, or a real-business conclusion.

## Business problem

Finance leadership needs a governed view of revenue, costs, profitability, cash flow, budget performance, working capital, and unusual transactions. This project makes those decisions traceable from signed ledger records through reusable calculations and visual reporting.

## Architecture

`Synthetic generator → raw CSV → audited cleaning → processed CSV → notebooks / Streamlit / PostgreSQL`

The processed directory is the shared source of truth. Negative revenue is retained and classified as a potential credit/refund; it is not automatically deleted.

## Dataset

The deterministic generator creates 2023–2025 activity, including transaction ledger records, customers, products, departments, vendors, budget, AR/AP, monthly cash flow, and monthly balance-sheet snapshots. `data/processed/data_dictionary.csv` documents each generated table after the pipeline runs.

## KPIs

| KPI | Formula |
|---|---|
| Gross profit | Revenue + COGS |
| Net profit | Revenue + COGS + operating expense + interest + tax |
| Net profit margin | Net profit / revenue |
| Current ratio | Current assets / current liabilities |
| Quick ratio | (Cash + AR) / current liabilities |
| Debt-to-equity | Total debt / equity |
| DSO | Average AR × 365 / revenue |
| Budget variance | Actual − budget |

Ratios are returned as unavailable when their denominator is zero. ROA/ROE use the latest available balance-sheet snapshot and must be interpreted with the selected income-statement period.

## Quick start (Windows 10/11)

```powershell
cd "C:\Users\MARWAT LAPTOP\Documents\Codex\2026-11-22\files-pasted-by-the-user-role\outputs\finance-data-analyst"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.data_ingestion
python scripts\build_notebooks.py
python -m pytest
python -m streamlit run dashboard\app.py
```

Always run these commands from the project directory. Using `python -m streamlit` avoids relying on the Scripts directory being on your Windows `PATH`.

Open the local URL reported by Streamlit. The dashboard provides date, department, product, region, and category filters plus downloadable filtered data and KPI summaries.

## PostgreSQL

Create a database, run `sql/schema.sql`, then run `sql/data_loading.sql` using `psql` from the project root so relative CSV paths resolve. Run `sql/financial_analysis.sql` for 22 documented examples, including joins, CTEs, windows, rankings, running totals, moving averages, margins, customer contribution, liquidity, and anomaly review.

## Portfolio talking points

- Signed accounting treatment preserves legitimate credits and reversals.
- Cleaning writes an audit record and flags, rather than silently deletes, unusual activity.
- The same processed data underpins Python, dashboard, and SQL analysis.
- Outlier detection is deliberately framed as a review signal—not an assertion of fraud.

## Deploy to Streamlit Community Cloud

Click the **Deploy on Streamlit Community Cloud** button above, sign in with GitHub, then choose the following settings:

| Setting | Value |
|---|---|
| Repository | `Waqaskhan23810/finance-data-analyst-project` |
| Branch | `main` |
| Entry point | `dashboard/app.py` |

After the first deployment, Streamlit provides a unique public `streamlit.app` URL. Add that URL to this README's deployment badge after it is live so recruiters can open the dashboard directly.

**Live app:** [https://finance-data-analyst-project-041.streamlit.app/](https://finance-data-analyst-project-041.streamlit.app/)

## Validation and deployment

Run `pytest` after generating data. Use `streamlit run dashboard/app.py` locally or deploy the repository to Streamlit Community Cloud with `dashboard/app.py` as the entrypoint; ensure the generated processed data is committed or generated in the deployment build step. For a production database, replace CSV loading with controlled ETL and credentialed connections.
