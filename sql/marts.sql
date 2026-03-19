DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_plan;
DROP TABLE IF EXISTS fct_revenue_monthly;
DROP TABLE IF EXISTS fct_customer_monthly_status;

CREATE TABLE dim_customer AS
SELECT DISTINCT
    customer_id,
    full_name,
    email,
    signup_date,
    country,
    acquisition_channel
FROM stg_customers;

CREATE TABLE dim_plan AS
SELECT DISTINCT
    plan_name,
    billing_cycle,
    monthly_price
FROM stg_subscriptions
ORDER BY monthly_price;

CREATE TABLE fct_revenue_monthly AS
WITH refund_by_payment AS (
    SELECT
        payment_id,
        ROUND(SUM(refund_amount), 2) AS total_refund_amount
    FROM stg_refunds
    GROUP BY payment_id
)
SELECT
    strftime('%Y-%m', p.payment_date) AS revenue_month,
    COUNT(DISTINCT CASE WHEN p.payment_status = 'paid' THEN p.customer_id END) AS paying_customers,
    ROUND(SUM(CASE WHEN p.payment_status = 'paid' THEN p.amount_paid ELSE 0 END), 2) AS gross_revenue,
    ROUND(SUM(COALESCE(r.total_refund_amount, 0)), 2) AS total_refunds,
    ROUND(
        SUM(CASE WHEN p.payment_status = 'paid' THEN p.amount_paid ELSE 0 END)
        - SUM(COALESCE(r.total_refund_amount, 0)),
        2
    ) AS net_revenue
FROM stg_payments p
LEFT JOIN refund_by_payment r
    ON p.payment_id = r.payment_id
GROUP BY strftime('%Y-%m', p.payment_date)
ORDER BY revenue_month;

CREATE TABLE fct_customer_monthly_status AS
WITH refund_by_payment AS (
    SELECT
        payment_id,
        ROUND(SUM(refund_amount), 2) AS total_refund_amount
    FROM stg_refunds
    GROUP BY payment_id
)
SELECT
    strftime('%Y-%m', i.billing_period_start) AS status_month,
    i.customer_id,
    i.subscription_id,
    s.plan_name,
    s.billing_cycle,
    s.monthly_price,
    i.invoice_id,
    i.invoice_status,
    COALESCE(p.payment_status, 'unpaid') AS payment_status,
    ROUND(i.amount_due, 2) AS amount_due,
    ROUND(COALESCE(p.amount_paid, 0), 2) AS amount_paid,
    ROUND(COALESCE(r.total_refund_amount, 0), 2) AS refund_amount,
    ROUND(COALESCE(p.amount_paid, 0) - COALESCE(r.total_refund_amount, 0), 2) AS net_revenue,
    CASE
        WHEN p.payment_status = 'paid' THEN 1
        ELSE 0
    END AS is_paid,
    CASE
        WHEN COALESCE(r.total_refund_amount, 0) > 0 THEN 1
        ELSE 0
    END AS is_refunded,
    CASE
        WHEN s.cancel_date IS NOT NULL
             AND strftime('%Y-%m', s.cancel_date) = strftime('%Y-%m', i.billing_period_start)
        THEN 1
        ELSE 0
    END AS is_cancelled_in_month,
    1 AS is_active_in_month
FROM stg_invoices i
LEFT JOIN stg_subscriptions s
    ON i.subscription_id = s.subscription_id
LEFT JOIN stg_payments p
    ON i.invoice_id = p.invoice_id
LEFT JOIN refund_by_payment r
    ON p.payment_id = r.payment_id
ORDER BY status_month, i.customer_id, i.subscription_id;