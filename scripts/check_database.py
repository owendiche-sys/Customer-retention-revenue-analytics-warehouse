import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "customer_analytics.db"

TABLES = [
    "raw_customers",
    "raw_subscriptions",
    "raw_invoices",
    "raw_payments",
    "raw_refunds",
    "stg_customers",
    "stg_subscriptions",
    "stg_invoices",
    "stg_payments",
    "stg_refunds",
    "dim_customer",
    "dim_plan",
    "fct_revenue_monthly",
    "fct_customer_monthly_status",
]


def print_table_count(cursor: sqlite3.Cursor, table_name: str) -> None:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count}")


def print_sample_rows(cursor: sqlite3.Cursor, table_name: str, limit: int = 5) -> None:
    print(f"\nSample rows from {table_name}:")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()

    if not rows:
        print("  No rows found.")
        return

    for row in rows:
        print(row)


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        print("TABLE COUNTS")
        print("-" * 40)
        for table in TABLES:
            print_table_count(cursor, table)

        print("\n" + "=" * 40)
        print_sample_rows(cursor, "fct_revenue_monthly")
        print_sample_rows(cursor, "fct_customer_monthly_status")

    finally:
        connection.close()


if __name__ == "__main__":
    main()