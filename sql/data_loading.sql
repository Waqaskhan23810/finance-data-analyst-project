-- Run from psql after copying processed CSV files to a server-accessible location.
\copy customers(customer_id,customer_name,region,segment) FROM 'data/processed/customers.csv' CSV HEADER;
\copy products(product_id,product_name,segment) FROM 'data/processed/products.csv' CSV HEADER;
\copy vendors(vendor_id,vendor_name,vendor_category) FROM 'data/processed/vendors.csv' CSV HEADER;
INSERT INTO departments(department_name) VALUES ('Sales'),('Operations'),('Engineering'),('Administration') ON CONFLICT DO NOTHING;
\copy transactions(transaction_id,transaction_date,category,department_name,product_id,customer_id,vendor_id,region,amount,currency,description,is_refund_or_reversal,amount_zscore,is_statistical_outlier) FROM 'data/processed/transactions.csv' CSV HEADER;
\copy cash_flow(flow_date,cash_flow_type,amount,description) FROM 'data/processed/cash_flow.csv' CSV HEADER;
\copy balance_sheet(snapshot_date,cash,accounts_receivable,inventory,accounts_payable,short_term_debt,total_debt,total_assets,equity) FROM 'data/processed/balance_sheet.csv' CSV HEADER;
