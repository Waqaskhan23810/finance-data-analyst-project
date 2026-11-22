-- 01 Monthly income statement
SELECT date_trunc('month',transaction_date) month, SUM(amount) FILTER (WHERE category='Revenue') revenue, SUM(amount) FILTER (WHERE category='COGS') cogs, SUM(amount) FILTER (WHERE category='Revenue' OR category='COGS') gross_profit FROM transactions GROUP BY 1 ORDER BY 1;
-- 02 Department operating expense
SELECT department_name, -SUM(amount) expense FROM transactions WHERE category='Operating Expense' GROUP BY 1 ORDER BY 2 DESC;
-- 03 Product revenue ranking
SELECT p.product_name,SUM(t.amount) revenue,DENSE_RANK() OVER(ORDER BY SUM(t.amount) DESC) rank FROM transactions t JOIN products p USING(product_id) WHERE category='Revenue' GROUP BY 1;
-- 04 Region revenue
SELECT region,SUM(amount) revenue FROM transactions WHERE category='Revenue' GROUP BY 1 ORDER BY 2 DESC;
-- 05 Quarterly P&L
SELECT date_trunc('quarter',transaction_date) quarter,SUM(amount) FILTER(WHERE category='Revenue') revenue,SUM(amount) net_profit FROM transactions GROUP BY 1 ORDER BY 1;
-- 06 Running revenue
SELECT transaction_date,amount,SUM(amount) OVER(ORDER BY transaction_date) running_revenue FROM transactions WHERE category='Revenue';
-- 07 Three-month moving revenue
WITH m AS (SELECT date_trunc('month',transaction_date) month,SUM(amount) revenue FROM transactions WHERE category='Revenue' GROUP BY 1) SELECT month,revenue,AVG(revenue) OVER(ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) moving_3m FROM m;
-- 08 MoM revenue growth
WITH m AS (SELECT date_trunc('month',transaction_date) month,SUM(amount) revenue FROM transactions WHERE category='Revenue' GROUP BY 1) SELECT month,revenue,(revenue/LAG(revenue) OVER(ORDER BY month))-1 mom_growth FROM m;
-- 09 YoY monthly revenue growth
WITH m AS (SELECT date_trunc('month',transaction_date) month,SUM(amount) revenue FROM transactions WHERE category='Revenue' GROUP BY 1) SELECT month,revenue,(revenue/LAG(revenue,12) OVER(ORDER BY month))-1 yoy_growth FROM m;
-- 10 Gross margin
SELECT SUM(amount) FILTER(WHERE category IN('Revenue','COGS'))/NULLIF(SUM(amount) FILTER(WHERE category='Revenue'),0) gross_margin FROM transactions;
-- 11 Operating margin
SELECT SUM(amount) FILTER(WHERE category IN('Revenue','COGS','Operating Expense'))/NULLIF(SUM(amount) FILTER(WHERE category='Revenue'),0) operating_margin FROM transactions;
-- 12 Net margin
SELECT SUM(amount)/NULLIF(SUM(amount) FILTER(WHERE category='Revenue'),0) net_margin FROM transactions;
-- 13 Cash flow by activity
SELECT date_trunc('quarter',flow_date) quarter,cash_flow_type,SUM(amount) cash_flow FROM cash_flow GROUP BY 1,2 ORDER BY 1,2;
-- 14 Month-end cash balance
SELECT flow_date,SUM(amount) OVER(ORDER BY flow_date) cumulative_change FROM cash_flow;
-- 15 Largest transactions for review
SELECT transaction_id,transaction_date,category,amount,description FROM transactions ORDER BY ABS(amount) DESC LIMIT 20;
-- 16 Credit notes/refunds
SELECT date_trunc('month',transaction_date) month,COUNT(*) credits,SUM(amount) credit_value FROM transactions WHERE category='Revenue' AND amount<0 GROUP BY 1;
-- 17 Customer contribution
SELECT c.customer_name,SUM(t.amount) revenue,100*SUM(t.amount)/SUM(SUM(t.amount)) OVER() contribution_pct FROM transactions t JOIN customers c USING(customer_id) WHERE category='Revenue' GROUP BY 1 ORDER BY 2 DESC;
-- 18 Top customer within each region
WITH x AS (SELECT c.region,c.customer_name,SUM(t.amount) revenue,RANK() OVER(PARTITION BY c.region ORDER BY SUM(t.amount) DESC) rnk FROM transactions t JOIN customers c USING(customer_id) WHERE category='Revenue' GROUP BY 1,2) SELECT * FROM x WHERE rnk<=3;
-- 19 Liquidity ratio by snapshot
SELECT snapshot_date,(cash+accounts_receivable+inventory)/NULLIF(accounts_payable+short_term_debt,0) current_ratio,(cash+accounts_receivable)/NULLIF(accounts_payable+short_term_debt,0) quick_ratio FROM balance_sheet;
-- 20 Debt-to-equity by snapshot
SELECT snapshot_date,total_debt/NULLIF(equity,0) debt_to_equity FROM balance_sheet;
-- 21 Expense share by department
SELECT department_name,-SUM(amount) expense,100*-SUM(amount)/SUM(-SUM(amount)) OVER() expense_share_pct FROM transactions WHERE category='Operating Expense' GROUP BY 1;
-- 22 Annual P&L
SELECT EXTRACT(YEAR FROM transaction_date) year,SUM(amount) FILTER(WHERE category='Revenue') revenue,SUM(amount) net_profit FROM transactions GROUP BY 1 ORDER BY 1;
