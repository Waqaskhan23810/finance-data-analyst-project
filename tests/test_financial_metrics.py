import pandas as pd
import numpy as np
from src.financial_metrics import safe_divide, income_statement_kpis

def test_safe_divide_handles_zero_and_missing():
    assert np.isnan(safe_divide(1, 0))
    assert np.isnan(safe_divide(1, None))

def test_income_statement_signed_ledger():
    frame = pd.DataFrame({"category":["Revenue","COGS","Operating Expense","Interest Expense","Income Tax"], "amount":[1000,-400,-200,-50,-70]})
    result = income_statement_kpis(frame)
    assert result["Gross Profit"] == 600
    assert result["Net Profit"] == 280
    assert result["Net Profit Margin"] == .28

def test_zero_revenue_margin_is_unavailable():
    frame = pd.DataFrame({"category":["COGS"], "amount":[-10]})
    assert np.isnan(income_statement_kpis(frame)["Net Profit Margin"])
