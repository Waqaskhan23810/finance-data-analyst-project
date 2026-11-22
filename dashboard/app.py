"""Meridian Industrial Systems — Financial Performance Intelligence dashboard."""
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import streamlit as st
from src.financial_metrics import income_statement_kpis, balance_sheet_kpis, cash_flow_kpis, budget_variance
from src.financial_analysis import monthly_performance, anomaly_transactions

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
st.set_page_config(page_title="Meridian Finance Intelligence", page_icon="📊", layout="wide")
st.markdown("<style>.block-container{padding-top:1.5rem}.stMetric{background:#f7f9fc;border-radius:10px;padding:12px}</style>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    frames = {}
    for name in ["transactions", "cash_flow", "balance_sheet", "accounts_receivable", "accounts_payable", "budget"]:
        frames[name] = pd.read_csv(DATA / f"{name}.csv")
    for name in ["transactions", "cash_flow", "balance_sheet"]:
        frames[name]["date"] = pd.to_datetime(frames[name]["date"])
    return frames

if not (DATA / "transactions.csv").exists():
    st.error("Processed data is missing. Run `python -m src.data_ingestion` from the project root first.")
    st.stop()
d = load_data()
tx = d["transactions"]
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date range", [tx.date.min().date(), tx.date.max().date()])
departments = st.sidebar.multiselect("Department", sorted(tx.department.dropna().unique()), default=sorted(tx.department.dropna().unique()))
products = st.sidebar.multiselect("Product", sorted(tx.product_id.dropna().unique()), default=sorted(tx.product_id.dropna().unique()))
regions = st.sidebar.multiselect("Region", sorted(tx.region.dropna().unique()), default=sorted(tx.region.dropna().unique()))
categories = st.sidebar.multiselect("Financial category", sorted(tx.category.unique()), default=sorted(tx.category.unique()))
filtered = tx.loc[tx.date.between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[-1])) & tx.department.isin(departments) & tx.category.isin(categories) & (tx.product_id.isna() | tx.product_id.isin(products)) & (tx.region.isna() | tx.region.isin(regions))].copy()
kpis = income_statement_kpis(filtered)
cash = cash_flow_kpis(d["cash_flow"].loc[d["cash_flow"].date.between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[-1]))])
st.title("Meridian Industrial Systems")
st.caption("Financial Performance Intelligence | Fictional company — synthetic data only")
cols = st.columns(6)
metric_specs = [("Revenue", kpis["Total Revenue"], "currency"), ("Operating expenses", kpis["Total Operating Expenses"], "currency"), ("Gross profit", kpis["Gross Profit"], "currency"), ("Net profit", kpis["Net Profit"], "currency"), ("Net margin", kpis["Net Profit Margin"], "percent"), ("Operating cash flow", cash["Operating Cash Flow"], "currency")]
for col, (label, value, kind) in zip(cols, metric_specs):
    display = f"${value:,.0f}" if kind == "currency" else f"{value:.1%}"
    col.metric(label, display)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Performance", "Expenses", "Cash & budget", "Financial health", "Risks & export"])
monthly = monthly_performance(filtered)
with tab1:
    st.plotly_chart(px.line(monthly, x="month", y=["Revenue", "gross_profit", "net_profit"], title="Monthly revenue and profitability", labels={"value":"USD", "month":"Month"}), width="stretch")
    st.plotly_chart(px.bar(filtered.loc[filtered.category.eq("Revenue")].groupby("product_id", as_index=False).amount.sum(), x="product_id", y="amount", title="Revenue by product"), width="stretch")
with tab2:
    expense = filtered.loc[filtered.category.eq("Operating Expense")].groupby("department", as_index=False).amount.sum()
    expense.amount = -expense.amount
    st.plotly_chart(px.bar(expense, x="department", y="amount", title="Operating expenses by department", labels={"amount":"USD"}), width="stretch")
with tab3:
    st.plotly_chart(px.bar(d["cash_flow"], x="date", y="amount", color="cash_flow_type", title="Cash flow by activity", barmode="relative"), width="stretch")
    variance = budget_variance(d["budget"], filtered)
    st.plotly_chart(px.bar(variance.groupby("department", as_index=False).variance.sum(), x="department", y="variance", title="Budget variance (actual less budget)"), width="stretch")
with tab4:
    health = balance_sheet_kpis(d["balance_sheet"], kpis, d["accounts_receivable"], d["accounts_payable"])
    st.dataframe(pd.DataFrame(health.items(), columns=["Metric", "Value"]), hide_index=True, width="stretch")
    st.caption("Ratios use latest balance-sheet snapshot and the selected-period income statement; interpret alongside period coverage.")
with tab5:
    flagged = anomaly_transactions(filtered)
    st.dataframe(flagged[["transaction_id", "date", "category", "amount", "description", "finding"]], hide_index=True, width="stretch")
    st.download_button("Download filtered transactions (CSV)", filtered.to_csv(index=False).encode(), "filtered_transactions.csv", "text/csv")
    st.download_button("Download KPI summary (CSV)", pd.DataFrame(kpis.items(), columns=["KPI", "Value"]).to_csv(index=False).encode(), "kpi_summary.csv", "text/csv")
