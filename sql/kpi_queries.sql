-- 1. Monthly revenue summary
SELECT
    revenue_month,
    paying_customers,
    gross_revenue,
    total_refunds,
    net_revenue
FROM fct_revenue_monthly
ORDER BY revenue_month;

-- 2. Total business summary
SELECT
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(net_revenue), 2) AS total_net_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_monthly_net_revenue
FROM fct_customer_monthly_status;

-- 3. Revenue by plan
SELECT
    plan_name,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(net_revenue), 2) AS total_net_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_revenue_per_record
FROM fct_customer_monthly_status
GROUP BY plan_name
ORDER BY total_net_revenue DESC;

-- 4. Monthly active customers
SELECT
    status_month,
    COUNT(DISTINCT customer_id) AS active_customers
FROM fct_customer_monthly_status
WHERE is_active_in_month = 1
GROUP BY status_month
ORDER BY status_month;

-- 5. Monthly cancellations
SELECT
    status_month,
    COUNT(DISTINCT customer_id) AS cancelled_customers
FROM fct_customer_monthly_status
WHERE is_cancelled_in_month = 1
GROUP BY status_month
ORDER BY status_month;

-- 6. Monthly churn rate
WITH monthly_active AS (
    SELECT
        status_month,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM fct_customer_monthly_status
    WHERE is_active_in_month = 1
    GROUP BY status_month
),
monthly_cancelled AS (
    SELECT
        status_month,
        COUNT(DISTINCT customer_id) AS cancelled_customers
    FROM fct_customer_monthly_status
    WHERE is_cancelled_in_month = 1
    GROUP BY status_month
)
SELECT
    a.status_month,
    a.active_customers,
    COALESCE(c.cancelled_customers, 0) AS cancelled_customers,
    ROUND(
        COALESCE(c.cancelled_customers, 0) * 100.0 / a.active_customers,
        2
    ) AS churn_rate_pct
FROM monthly_active a
LEFT JOIN monthly_cancelled c
    ON a.status_month = c.status_month
ORDER BY a.status_month;

-- 7. Average revenue per paying customer by month
SELECT
    revenue_month,
    paying_customers,
    net_revenue,
    ROUND(net_revenue * 1.0 / paying_customers, 2) AS arppu
FROM fct_revenue_monthly
WHERE paying_customers > 0
ORDER BY revenue_month;

-- 8. Simple customer lifetime value by plan
SELECT
    plan_name,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(AVG(customer_lifetime_value), 2) AS avg_ltv
FROM (
    SELECT
        customer_id,
        plan_name,
        SUM(net_revenue) AS customer_lifetime_value
    FROM fct_customer_monthly_status
    GROUP BY customer_id, plan_name
) t
GROUP BY plan_name
ORDER BY avg_ltv DESC;