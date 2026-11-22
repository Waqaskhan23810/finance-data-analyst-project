"""Validated financial KPI calculations used by notebooks and dashboard."""
from __future__ import annotations
import numpy as np
import pandas as pd

def safe_divide(numerator: float, denominator: float) -> float:
    """Return NaN for unavailable ratios instead of raising or inventing a value."""
    if denominator is None or pd.isna(denominator) or denominator == 0:
        return np.nan
    return float(numerator) / float(denominator)

def income_statement_kpis(transactions: pd.DataFrame) -> dict[str, float]:
    """Calculate period KPIs from signed ledger amounts and named categories."""
    frame = transactions.copy()
    revenue = frame.loc[frame.category.eq("Revenue"), "amount"].sum()
    cogs = frame.loc[frame.category.eq("COGS"), "amount"].sum()
    opex = frame.loc[frame.category.eq("Operating Expense"), "amount"].sum()
    interest = frame.loc[frame.category.eq("Interest Expense"), "amount"].sum()
    tax = frame.loc[frame.category.eq("Income Tax"), "amount"].sum()
    gross_profit = revenue + cogs
    operating_profit = gross_profit + opex
    net_profit = operating_profit + interest + tax
    return {
        "Total Revenue": revenue, "COGS": cogs, "Total Operating Expenses": -opex,
        "Gross Profit": gross_profit, "Operating Profit": operating_profit,
        "Net Profit": net_profit, "Gross Profit Margin": safe_divide(gross_profit, revenue),
        "Operating Profit Margin": safe_divide(operating_profit, revenue),
        "Net Profit Margin": safe_divide(net_profit, revenue),
        "Expense-to-Revenue Ratio": safe_divide(-opex, revenue),
    }

def balance_sheet_kpis(balance_sheet: pd.DataFrame, income: dict[str, float], ar: pd.DataFrame, ap: pd.DataFrame) -> dict[str, float]:
    """Calculate point-in-time liquidity, leverage, and working-capital metrics."""
    if balance_sheet.empty:
        return {}
    latest = balance_sheet.sort_values("date").iloc[-1]
    current_assets = latest["cash"] + latest["accounts_receivable"] + latest["inventory"]
    current_liabilities = latest["accounts_payable"] + latest["short_term_debt"]
    avg_ar = ar["open_amount"].mean() if not ar.empty else np.nan
    avg_ap = ap["open_amount"].mean() if not ap.empty else np.nan
    purchases = abs(income["COGS"])
    return {
        "Current Ratio": safe_divide(current_assets, current_liabilities),
        "Quick Ratio": safe_divide(latest["cash"] + latest["accounts_receivable"], current_liabilities),
        "Working Capital": current_assets - current_liabilities,
        "Debt-to-Equity Ratio": safe_divide(latest["total_debt"], latest["equity"]),
        "ROA": safe_divide(income["Net Profit"], latest["total_assets"]),
        "ROE": safe_divide(income["Net Profit"], latest["equity"]),
        "AR Turnover": safe_divide(income["Total Revenue"], avg_ar),
        "AP Turnover": safe_divide(purchases, avg_ap),
        "DSO": safe_divide(avg_ar * 365, income["Total Revenue"]),
    }

def cash_flow_kpis(cash_flow: pd.DataFrame) -> dict[str, float]:
    grouped = cash_flow.groupby("cash_flow_type", as_index=True)["amount"].sum()
    operating = grouped.get("Operating", 0.0)
    investing = grouped.get("Investing", 0.0)
    financing = grouped.get("Financing", 0.0)
    return {"Operating Cash Flow": operating, "Investing Cash Flow": investing,
            "Financing Cash Flow": financing, "Net Cash Flow": operating + investing + financing}

def budget_variance(budget: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
    actual = (transactions.assign(month=transactions["date"].dt.to_period("M").astype(str))
              .groupby(["month", "department", "category"], as_index=False)["amount"].sum())
    result = budget.merge(actual, how="left", on=["month", "department", "category"], suffixes=("_budget", "_actual"))
    result["amount_actual"] = result["amount_actual"].fillna(0)
    result["variance"] = result["amount_actual"] - result["amount_budget"]
    result["variance_pct"] = result.apply(lambda x: safe_divide(x.variance, x.amount_budget), axis=1)
    return result
