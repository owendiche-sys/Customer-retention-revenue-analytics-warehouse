DROP TABLE IF EXISTS stg_customers;
DROP TABLE IF EXISTS stg_subscriptions;
DROP TABLE IF EXISTS stg_invoices;
DROP TABLE IF EXISTS stg_payments;
DROP TABLE IF EXISTS stg_refunds;

CREATE TABLE stg_customers AS
SELECT
    TRIM(customer_id) AS customer_id,
    TRIM(full_name) AS full_name,
    LOWER(TRIM(email)) AS email,
    DATE(signup_date) AS signup_date,
    TRIM(country) AS country,
    TRIM(acquisition_channel) AS acquisition_channel
FROM raw_customers;

CREATE TABLE stg_subscriptions AS
SELECT
    TRIM(subscription_id) AS subscription_id,
    TRIM(customer_id) AS customer_id,
    TRIM(plan_name) AS plan_name,
    DATE(start_date) AS start_date,
    CASE
        WHEN TRIM(end_date) = '' THEN NULL
        ELSE DATE(end_date)
    END AS end_date,
    ROUND(monthly_price, 2) AS monthly_price,
    LOWER(TRIM(billing_cycle)) AS billing_cycle,
    LOWER(TRIM(subscription_status)) AS subscription_status,
    CASE
        WHEN TRIM(cancel_date) = '' THEN NULL
        ELSE DATE(cancel_date)
    END AS cancel_date
FROM raw_subscriptions;

CREATE TABLE stg_invoices AS
SELECT
    TRIM(invoice_id) AS invoice_id,
    TRIM(customer_id) AS customer_id,
    TRIM(subscription_id) AS subscription_id,
    DATE(invoice_date) AS invoice_date,
    DATE(billing_period_start) AS billing_period_start,
    DATE(billing_period_end) AS billing_period_end,
    ROUND(amount_due, 2) AS amount_due,
    LOWER(TRIM(invoice_status)) AS invoice_status
FROM raw_invoices;

CREATE TABLE stg_payments AS
SELECT
    TRIM(payment_id) AS payment_id,
    TRIM(invoice_id) AS invoice_id,
    TRIM(customer_id) AS customer_id,
    DATE(payment_date) AS payment_date,
    ROUND(amount_paid, 2) AS amount_paid,
    LOWER(TRIM(payment_method)) AS payment_method,
    LOWER(TRIM(payment_status)) AS payment_status
FROM raw_payments;

CREATE TABLE stg_refunds AS
SELECT
    TRIM(refund_id) AS refund_id,
    TRIM(payment_id) AS payment_id,
    TRIM(customer_id) AS customer_id,
    DATE(refund_date) AS refund_date,
    ROUND(refund_amount, 2) AS refund_amount,
    TRIM(refund_reason) AS refund_reason
FROM raw_refunds;