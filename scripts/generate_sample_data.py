from __future__ import annotations

import random
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

PLAN_PRICES = {
    "Basic": 19.99,
    "Pro": 49.99,
    "Premium": 89.99,
}

CHANNELS = ["Organic Search", "Paid Ads", "Referral", "Social Media", "Direct"]
COUNTRIES = ["UK", "USA", "Canada", "Germany", "Nigeria"]
PAYMENT_METHODS = ["card", "paypal", "bank_transfer"]
REFUND_REASONS = ["billing error", "service issue", "duplicate payment", "customer request"]


def random_date(start: date, end: date) -> date:
    """Return a random date between start and end inclusive."""
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def month_end(dt: date) -> date:
    """Return the last day of the month for dt."""
    return date(dt.year, dt.month, monthrange(dt.year, dt.month)[1])


def add_months(dt: date, months: int) -> date:
    """Add months to a date while keeping a valid day."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, monthrange(year, month)[1])
    return date(year, month, day)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    customers = []
    subscriptions = []
    invoices = []
    payments = []
    refunds = []

    first_names = [
        "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin",
        "Lucas", "Henry", "Alexander", "Mia", "Olivia", "Ava", "Sophia",
        "Isabella", "Amelia", "Harper", "Evelyn", "Ella", "Grace"
    ]
    last_names = [
        "Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas",
        "Jackson", "White", "Harris", "Martin", "Clark", "Lewis"
    ]

    analysis_cutoff = date(2025, 12, 31)
    num_customers = 120

    invoice_counter = 1
    payment_counter = 1
    refund_counter = 1

    for i in range(1, num_customers + 1):
        customer_id = f"CUST{i:04d}"
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = full_name.lower().replace(" ", ".") + f"{i}@example.com"
        signup_date = random_date(date(2024, 1, 1), date(2025, 6, 30))
        country = random.choice(COUNTRIES)
        acquisition_channel = random.choice(CHANNELS)

        customers.append(
            {
                "customer_id": customer_id,
                "full_name": full_name,
                "email": email,
                "signup_date": signup_date.isoformat(),
                "country": country,
                "acquisition_channel": acquisition_channel,
            }
        )

        subscription_id = f"SUB{i:04d}"
        plan_name = random.choices(
            population=["Basic", "Pro", "Premium"],
            weights=[0.5, 0.35, 0.15],
            k=1,
        )[0]
        monthly_price = PLAN_PRICES[plan_name]
        start_date = signup_date + timedelta(days=random.randint(0, 10))

        cancelled = random.random() < 0.28
        cancel_date = None
        end_date = None
        subscription_status = "active"

        if cancelled:
            active_months = random.randint(2, 10)
            cancel_date = add_months(start_date, active_months)
            if cancel_date > analysis_cutoff:
                cancel_date = None
            else:
                end_date = cancel_date
                subscription_status = "cancelled"

        subscriptions.append(
            {
                "subscription_id": subscription_id,
                "customer_id": customer_id,
                "plan_name": plan_name,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else "",
                "monthly_price": monthly_price,
                "billing_cycle": "monthly",
                "subscription_status": subscription_status,
                "cancel_date": cancel_date.isoformat() if cancel_date else "",
            }
        )

        # Generate monthly invoices until cancellation or analysis cutoff
        invoice_date = start_date
        month_idx = 0

        while invoice_date <= analysis_cutoff:
            if cancel_date and invoice_date > cancel_date:
                break

            billing_start = add_months(start_date, month_idx)
            if billing_start > analysis_cutoff:
                break

            billing_end = month_end(billing_start)

            invoice_id = f"INV{invoice_counter:05d}"
            payment_id = f"PAY{payment_counter:05d}"

            invoice_status = "paid" if random.random() < 0.92 else "failed"
            amount_due = monthly_price

            invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "subscription_id": subscription_id,
                    "invoice_date": billing_start.isoformat(),
                    "billing_period_start": billing_start.isoformat(),
                    "billing_period_end": billing_end.isoformat(),
                    "amount_due": amount_due,
                    "invoice_status": invoice_status,
                }
            )

            if invoice_status == "paid":
                payment_date = billing_start + timedelta(days=random.randint(0, 5))
                amount_paid = amount_due
                payment_status = "paid"
            else:
                payment_date = billing_start + timedelta(days=random.randint(1, 7))
                amount_paid = 0.0
                payment_status = "failed"

            payments.append(
                {
                    "payment_id": payment_id,
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "payment_date": payment_date.isoformat(),
                    "amount_paid": amount_paid,
                    "payment_method": random.choice(PAYMENT_METHODS),
                    "payment_status": payment_status,
                }
            )

            # Create refunds for a small fraction of successful payments
            if payment_status == "paid" and random.random() < 0.06:
                refund_amount = round(amount_paid * random.choice([0.25, 0.5, 1.0]), 2)
                refund_date = payment_date + timedelta(days=random.randint(3, 20))

                refunds.append(
                    {
                        "refund_id": f"REF{refund_counter:05d}",
                        "payment_id": payment_id,
                        "customer_id": customer_id,
                        "refund_date": refund_date.isoformat(),
                        "refund_amount": refund_amount,
                        "refund_reason": random.choice(REFUND_REASONS),
                    }
                )
                refund_counter += 1

            invoice_counter += 1
            payment_counter += 1
            month_idx += 1
            invoice_date = add_months(start_date, month_idx)

    pd.DataFrame(customers).to_csv(RAW_DIR / "customers.csv", index=False)
    pd.DataFrame(subscriptions).to_csv(RAW_DIR / "subscriptions.csv", index=False)
    pd.DataFrame(invoices).to_csv(RAW_DIR / "invoices.csv", index=False)
    pd.DataFrame(payments).to_csv(RAW_DIR / "payments.csv", index=False)
    pd.DataFrame(refunds).to_csv(RAW_DIR / "refunds.csv", index=False)

    print("Sample CSV files created successfully.")
    print(f"Saved to: {RAW_DIR}")


if __name__ == "__main__":
    main()