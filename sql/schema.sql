CREATE TABLE departments (department_id serial PRIMARY KEY, department_name text UNIQUE NOT NULL);
CREATE TABLE customers (customer_id text PRIMARY KEY, customer_name text NOT NULL, region text NOT NULL, segment text NOT NULL);
CREATE TABLE products (product_id text PRIMARY KEY, product_name text NOT NULL, segment text NOT NULL);
CREATE TABLE vendors (vendor_id text PRIMARY KEY, vendor_name text NOT NULL, vendor_category text NOT NULL);
CREATE TABLE transactions (transaction_id text PRIMARY KEY, transaction_date date NOT NULL, category text NOT NULL CHECK(category IN ('Revenue','COGS','Operating Expense','Interest Expense','Income Tax')), department_name text NOT NULL REFERENCES departments(department_name), product_id text REFERENCES products(product_id), customer_id text REFERENCES customers(customer_id), vendor_id text REFERENCES vendors(vendor_id), region text, amount numeric(14,2) NOT NULL, currency char(3) NOT NULL DEFAULT 'USD', description text, is_refund_or_reversal boolean, amount_zscore numeric(12,6), is_statistical_outlier boolean);
CREATE TABLE cash_flow (cash_flow_id bigserial PRIMARY KEY, flow_date date NOT NULL, cash_flow_type text CHECK(cash_flow_type IN ('Operating','Investing','Financing')), amount numeric(14,2) NOT NULL, description text);
CREATE TABLE balance_sheet (snapshot_date date PRIMARY KEY, cash numeric(14,2), accounts_receivable numeric(14,2), inventory numeric(14,2), accounts_payable numeric(14,2), short_term_debt numeric(14,2), total_debt numeric(14,2), total_assets numeric(14,2), equity numeric(14,2));
CREATE INDEX ix_transactions_date ON transactions(transaction_date);
CREATE INDEX ix_transactions_category ON transactions(category);
