"""Auditable data quality checks and processing for finance records."""
from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd

LOGGER = logging.getLogger(__name__)

def assess_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    checks = {
        "rows": len(frame), "duplicate_transaction_ids": int(frame.transaction_id.duplicated().sum()),
        "missing_cells": int(frame.isna().sum().sum()), "invalid_dates": int(pd.to_datetime(frame.date, errors="coerce").isna().sum()),
        "zero_amounts": int(frame.amount.eq(0).sum()), "negative_amounts": int(frame.amount.lt(0).sum()),
        "currencies": int(frame.currency.nunique()),
    }
    return pd.DataFrame(checks.items(), columns=["check", "value"])

def clean_transactions(frame: pd.DataFrame, audit_path: Path | None = None) -> pd.DataFrame:
    """Standardize records without discarding legitimate signed accounting entries."""
    clean = frame.copy()
    clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
    before = len(clean)
    clean = clean.dropna(subset=["transaction_id", "date", "amount", "category"])
    clean = clean.drop_duplicates(subset="transaction_id", keep="first")
    clean["department"] = clean["department"].str.strip().str.title()
    clean["currency"] = clean["currency"].str.upper().str.strip()
    clean["is_refund_or_reversal"] = clean["amount"].lt(0) & clean["category"].eq("Revenue")
    clean["amount_zscore"] = (clean.amount - clean.amount.mean()) / clean.amount.std(ddof=0)
    clean["is_statistical_outlier"] = clean.amount_zscore.abs().gt(3)
    if audit_path:
        pd.DataFrame([{"operation": "removed invalid/duplicate records", "rows_before": before, "rows_after": len(clean),
                       "negative_entries_retained": int(clean.amount.lt(0).sum())}]).to_csv(audit_path, index=False)
    LOGGER.info("Cleaned %s records to %s", before, len(clean))
    return clean
