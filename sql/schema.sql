PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS raw_customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    signup_date TEXT,
    country TEXT,
    acquisition_channel TEXT
);

CREATE TABLE IF NOT EXISTS raw_subscriptions (
    subscription_id TEXT PRIMARY KEY,
    customer_id TEXT,
    plan_name TEXT,
    start_date TEXT,
    end_date TEXT,
    monthly_price REAL,
    billing_cycle TEXT,
    subscription_status TEXT,
    cancel_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
);

CREATE TABLE IF NOT EXISTS raw_invoices (
    invoice_id TEXT PRIMARY KEY,
    customer_id TEXT,
    subscription_id TEXT,
    invoice_date TEXT,
    billing_period_start TEXT,
    billing_period_end TEXT,
    amount_due REAL,
    invoice_status TEXT,
    FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id),
    FOREIGN KEY (subscription_id) REFERENCES raw_subscriptions(subscription_id)
);

CREATE TABLE IF NOT EXISTS raw_payments (
    payment_id TEXT PRIMARY KEY,
    invoice_id TEXT,
    customer_id TEXT,
    payment_date TEXT,
    amount_paid REAL,
    payment_method TEXT,
    payment_status TEXT,
    FOREIGN KEY (invoice_id) REFERENCES raw_invoices(invoice_id),
    FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
);

CREATE TABLE IF NOT EXISTS raw_refunds (
    refund_id TEXT PRIMARY KEY,
    payment_id TEXT,
    customer_id TEXT,
    refund_date TEXT,
    refund_amount REAL,
    refund_reason TEXT,
    FOREIGN KEY (payment_id) REFERENCES raw_payments(payment_id),
    FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
);