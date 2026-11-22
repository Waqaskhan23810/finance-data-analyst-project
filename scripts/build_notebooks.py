"""Create six executable, beginner-friendly notebooks without hand-maintained JSON."""
from pathlib import Path
import sys
import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"; NB.mkdir(exist_ok=True)
shared = """from pathlib import Path\nimport sys\nROOT = Path.cwd().resolve().parent if Path.cwd().name == 'notebooks' else Path.cwd()\nsys.path.append(str(ROOT))\nimport pandas as pd\nfrom src.data_ingestion import build_data\nfrom src.financial_metrics import income_statement_kpis, budget_variance\nfrom src.financial_analysis import monthly_performance, anomaly_transactions\ndata = build_data()\ntx = data['transactions']\n"""
specs = [
("01_financial_data_assessment", "Financial Data Assessment", "Assess dimensions, types, missingness, duplicate IDs, signed values, currencies, dates and outliers before trusting finance analysis.", "from src.data_cleaning import assess_transactions\nassessment = assess_transactions(tx)\nassessment"),
("02_financial_data_cleaning", "Financial Data Cleaning", "Cleaning retains negative entries because they may be credit notes or reversals; the process creates an audit trail.", "tx[['transaction_id','date','category','amount','is_refund_or_reversal','is_statistical_outlier']].head()"),
("03_financial_eda", "Financial Exploratory Analysis", "Examine monthly revenue, costs and net profit. Interpret movement as observed performance, not a causal conclusion.", "monthly = monthly_performance(tx)\nmonthly[['month','Revenue','gross_profit','net_profit','net_margin']].tail(12)"),
("04_financial_kpi_analysis", "Financial KPI Analysis", "Formula example: net margin = net profit / revenue. A missing denominator makes the ratio unavailable, not zero.", "pd.DataFrame(income_statement_kpis(tx).items(), columns=['KPI','Value'])"),
("05_financial_performance_analysis", "Financial Performance Analysis", "Compare actual ledger activity with budget; a variance is actual less budget and should be interpreted based on whether the line is revenue or cost.", "variance = budget_variance(data['budget'], tx)\nvariance.groupby('department',as_index=False)['variance'].sum()"),
("06_advanced_financial_analysis", "Advanced Financial Analysis", "Statistical outliers prioritize entries for review. They are not confirmation of fraud, error, or misconduct.", "anomaly_transactions(tx)[['transaction_id','date','category','amount','finding']].head(10)"),
]
if len(sys.argv) > 1:
    requested = sys.argv[1].replace('.ipynb', '')
    specs = [spec for spec in specs if spec[0] == requested]
    if not specs:
        raise SystemExit(f'Unknown notebook: {requested}')
for filename,title,intro,analysis in specs:
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(f'# {title}\n\n**Objective.** {intro}\n\nThis notebook uses synthetic data for Meridian Industrial Systems.'), nbf.v4.new_code_cell(shared), nbf.v4.new_code_cell(analysis), nbf.v4.new_markdown_cell('## Conclusion\nResults should be reconciled with source ledgers and reviewed in context before management action.')]
    client = NotebookClient(nb, timeout=120, kernel_name="python3")
    client.execute(cwd=str(ROOT))
    nbf.write(nb, NB / f'{filename}.ipynb')
print(f'Created {len(specs)} notebooks in {NB}')
