"""Create reproducible synthetic data for the fictional Meridian Industrial Systems."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, RANDOM_SEED
from src.data_cleaning import clean_transactions

DEPARTMENTS = ["Sales", "Operations", "Engineering", "Administration"]
PRODUCTS = [("P100", "Industrial Pumps", "Industrial"), ("P200", "Control Valves", "Industrial"),
            ("P300", "Monitoring Sensors", "Technology"), ("P400", "Service Contracts", "Services")]
REGIONS = ["North", "South", "East", "West"]

def _directories() -> None:
    for path in [RAW_DIR, PROCESSED_DIR]: path.mkdir(parents=True, exist_ok=True)

def generate_datasets() -> dict[str, pd.DataFrame]:
    """Generate transparent, plausible—not real-company—operating data for 2023–2025."""
    rng = np.random.default_rng(RANDOM_SEED)
    dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    customers = pd.DataFrame({"customer_id": [f"C{i:03d}" for i in range(1, 61)],
                              "customer_name": [f"Client {i:02d}" for i in range(1, 61)],
                              "region": rng.choice(REGIONS, 60), "segment": rng.choice(["Enterprise", "Mid-Market", "Distributor"], 60)})
    products = pd.DataFrame(PRODUCTS, columns=["product_id", "product_name", "segment"])
    vendors = pd.DataFrame({"vendor_id": [f"V{i:03d}" for i in range(1, 21)], "vendor_name": [f"Supplier {i:02d}" for i in range(1, 21)], "vendor_category": rng.choice(["Materials", "Freight", "Professional Services", "Facilities"], 20)})
    rows, tid = [], 1
    # Sales ledger including a small number of legitimate credit notes.
    for month_idx, month in enumerate(pd.date_range("2023-01-01", "2025-12-01", freq="MS")):
        growth = 1 + month_idx * 0.008
        for _ in range(70):
            product = products.iloc[rng.integers(len(products))]
            customer = customers.iloc[rng.integers(len(customers))]
            date = month + pd.Timedelta(days=int(rng.integers(0, 28)))
            revenue = round(rng.uniform(2500, 16000) * growth, 2)
            if rng.random() < .025: revenue *= -1
            rows.append([f"T{tid:06d}", date, "Revenue", "Sales", product.product_id, customer.customer_id, None, customer.region, revenue, "USD", "Customer invoice or credit note"]); tid += 1
            if revenue > 0:
                rows.append([f"T{tid:06d}", date, "COGS", "Operations", product.product_id, customer.customer_id, None, customer.region, round(-revenue*rng.uniform(.42,.56),2), "USD", "Manufacturing cost"]); tid += 1
        for department in DEPARTMENTS:
            spend = rng.uniform(28000, 65000) * (1 + month_idx*.004)
            rows.append([f"T{tid:06d}", month + pd.Timedelta(days=15), "Operating Expense", department, None, None, f"V{rng.integers(1,21):03d}", None, round(-spend,2), "USD", "Operating expenditure"]); tid += 1
        rows.extend([[f"T{tid:06d}", month + pd.Timedelta(days=28), "Interest Expense", "Administration", None, None, "V001", None, round(-rng.uniform(4000,6500),2), "USD", "Debt interest"],
                     [f"T{tid+1:06d}", month + pd.Timedelta(days=28), "Income Tax", "Administration", None, None, "V002", None, round(-rng.uniform(10000,24000),2), "USD", "Estimated income tax"]]); tid += 2
    transactions = pd.DataFrame(rows, columns=["transaction_id","date","category","department","product_id","customer_id","vendor_id","region","amount","currency","description"])
    monthly = pd.date_range("2023-01-31", "2025-12-31", freq="ME")
    cash_flow = pd.DataFrame([{ "date": d, "cash_flow_type": typ, "amount": round(amt,2), "description": desc}
        for d in monthly for typ, amt, desc in [("Operating", rng.uniform(100000,230000), "Cash generated from operations"), ("Investing", -rng.uniform(25000,90000), "Equipment and systems investment"), ("Financing", rng.uniform(-35000,40000), "Debt and equity financing")]])
    balance = []; cash = 550000
    for d in monthly:
        cash += cash_flow.loc[cash_flow.date.eq(d), "amount"].sum()
        ar, inventory, ap, debt = rng.uniform(350000,600000), rng.uniform(450000,700000), rng.uniform(220000,390000), rng.uniform(700000,900000)
        assets = cash + ar + inventory + 750000
        balance.append([d, round(cash,2), round(ar,2), round(inventory,2), round(ap,2), 180000, round(debt,2), round(assets,2), round(assets-ap-180000-debt,2)])
    balance_sheet = pd.DataFrame(balance, columns=["date","cash","accounts_receivable","inventory","accounts_payable","short_term_debt","total_debt","total_assets","equity"])
    ar = pd.DataFrame({"invoice_id": [f"AR{i:04d}" for i in range(1,121)], "customer_id": rng.choice(customers.customer_id,120), "invoice_date": rng.choice(dates,120), "due_date": rng.choice(dates,120), "open_amount": rng.uniform(2000,30000,120).round(2), "status": rng.choice(["Current","Overdue"],120,p=[.72,.28])})
    ap = pd.DataFrame({"bill_id": [f"AP{i:04d}" for i in range(1,101)], "vendor_id": rng.choice(vendors.vendor_id,100), "bill_date": rng.choice(dates,100), "due_date": rng.choice(dates,100), "open_amount": rng.uniform(1500,24000,100).round(2), "status": rng.choice(["Current","Overdue"],100,p=[.78,.22])})
    budget = []
    for d in pd.date_range("2023-01-01","2025-12-01",freq="MS"):
        for dept in DEPARTMENTS:
            budget.append([str(d.to_period("M")),dept,"Operating Expense",round(-rng.uniform(30000,65000),2)])
        budget.append([str(d.to_period("M")),"Sales","Revenue",round(rng.uniform(600000,850000),2)])
    return {"customers":customers,"products":products,"vendors":vendors,"transactions":transactions,"cash_flow":cash_flow,"balance_sheet":balance_sheet,"accounts_receivable":ar,"accounts_payable":ap,"budget":pd.DataFrame(budget,columns=["month","department","category","amount"])}

def build_data() -> dict[str, pd.DataFrame]:
    _directories(); datasets = generate_datasets()
    for name, frame in datasets.items(): frame.to_csv(RAW_DIR / f"{name}.csv", index=False)
    clean = clean_transactions(datasets["transactions"], PROCESSED_DIR / "cleaning_audit.csv")
    datasets["transactions"] = clean
    for name, frame in datasets.items(): frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
    pd.DataFrame([{"dataset": k, "rows": len(v), "business_meaning": {"transactions":"Signed general-ledger activity; negative revenue can be credits/refunds.","cash_flow":"Monthly operating, investing, and financing cash movements.","balance_sheet":"Month-end financial position.","budget":"Monthly budget by department/category."}.get(k,"Master or subledger dimension table.")} for k,v in datasets.items()]).to_csv(PROCESSED_DIR / "data_dictionary.csv", index=False)
    return datasets

if __name__ == "__main__": build_data()
