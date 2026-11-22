from __future__ import annotations
import pandas as pd

def monthly_performance(transactions: pd.DataFrame) -> pd.DataFrame:
    frame = transactions.copy(); frame["month"] = frame.date.dt.to_period("M").dt.to_timestamp()
    pivot = frame.pivot_table(index="month", columns="category", values="amount", aggfunc="sum", fill_value=0)
    for col in ["Revenue","COGS","Operating Expense","Interest Expense","Income Tax"]:
        if col not in pivot: pivot[col] = 0
    pivot["gross_profit"] = pivot["Revenue"] + pivot["COGS"]
    pivot["net_profit"] = pivot["gross_profit"] + pivot["Operating Expense"] + pivot["Interest Expense"] + pivot["Income Tax"]
    pivot["net_margin"] = pivot["net_profit"] / pivot["Revenue"].replace(0, float("nan"))
    pivot["revenue_mom"] = pivot["Revenue"].pct_change()
    pivot["revenue_yoy"] = pivot["Revenue"].pct_change(12)
    return pivot.reset_index()

def anomaly_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    flagged = transactions.loc[transactions.is_statistical_outlier].copy()
    flagged["finding"] = "Statistical outlier: requires review; not evidence of fraud or error."
    return flagged.sort_values("amount", key=lambda s: s.abs(), ascending=False)
