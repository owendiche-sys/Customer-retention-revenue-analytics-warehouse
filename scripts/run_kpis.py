import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "customer_analytics.db"


QUERIES = {
    "monthly_revenue": """
        SELECT
            revenue_month,
            paying_customers,
            gross_revenue,
            total_refunds,
            net_revenue
        FROM fct_revenue_monthly
        ORDER BY revenue_month;
    """,
    "business_summary": """
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            ROUND(SUM(net_revenue), 2) AS total_net_revenue,
            ROUND(AVG(net_revenue), 2) AS avg_monthly_net_revenue
        FROM fct_customer_monthly_status;
    """,
    "revenue_by_plan": """
        SELECT
            plan_name,
            COUNT(DISTINCT customer_id) AS customers,
            ROUND(SUM(net_revenue), 2) AS total_net_revenue,
            ROUND(AVG(net_revenue), 2) AS avg_revenue_per_record
        FROM fct_customer_monthly_status
        GROUP BY plan_name
        ORDER BY total_net_revenue DESC;
    """,
    "monthly_churn": """
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
    """,
    "ltv_by_plan": """
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
    """
}


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        for name, query in QUERIES.items():
            print("\n" + "=" * 60)
            print(name.upper())
            print("=" * 60)
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows[:10]:
                print(row)

            if len(rows) > 10:
                print(f"... showing first 10 of {len(rows)} rows")

    finally:
        connection.close()


if __name__ == "__main__":
    main()