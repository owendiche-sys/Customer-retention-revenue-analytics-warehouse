from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "customer_analytics.db"


@st.cache_data
def run_query(query: str) -> pd.DataFrame:
    connection = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


@st.cache_data
def load_base_data() -> pd.DataFrame:
    query = """
    SELECT
        f.status_month,
        f.customer_id,
        f.subscription_id,
        f.plan_name,
        f.billing_cycle,
        f.monthly_price,
        f.invoice_id,
        f.invoice_status,
        f.payment_status,
        f.amount_due,
        f.amount_paid,
        f.refund_amount,
        f.net_revenue,
        f.is_paid,
        f.is_refunded,
        f.is_cancelled_in_month,
        f.is_active_in_month,
        c.full_name,
        c.signup_date,
        c.country,
        c.acquisition_channel
    FROM fct_customer_monthly_status f
    LEFT JOIN dim_customer c
        ON f.customer_id = c.customer_id
    ORDER BY f.status_month, f.customer_id, f.subscription_id;
    """
    df = run_query(query)

    numeric_cols = [
        "monthly_price",
        "amount_due",
        "amount_paid",
        "refund_amount",
        "net_revenue",
        "is_paid",
        "is_refunded",
        "is_cancelled_in_month",
        "is_active_in_month",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    text_cols = [
        "status_month",
        "customer_id",
        "subscription_id",
        "plan_name",
        "billing_cycle",
        "invoice_id",
        "invoice_status",
        "payment_status",
        "full_name",
        "signup_date",
        "country",
        "acquisition_channel",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


def format_currency(value: float) -> str:
    return f"£{value:,.2f}"


def build_monthly_metrics(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("status_month", as_index=False)
        .agg(
            active_customers=("customer_id", "nunique"),
            paying_customers=("customer_id", lambda s: s[df.loc[s.index, "is_paid"] == 1].nunique()),
            gross_revenue=("amount_paid", "sum"),
            total_refunds=("refund_amount", "sum"),
            net_revenue=("net_revenue", "sum"),
            cancelled_customers=("customer_id", lambda s: s[df.loc[s.index, "is_cancelled_in_month"] == 1].nunique()),
        )
        .sort_values("status_month")
    )

    monthly["churn_rate_pct"] = (
        monthly["cancelled_customers"] * 100.0 / monthly["active_customers"]
    ).round(2)

    monthly["arppu"] = (
        monthly["net_revenue"] / monthly["paying_customers"].replace(0, pd.NA)
    ).round(2)

    monthly["gross_revenue"] = monthly["gross_revenue"].round(2)
    monthly["total_refunds"] = monthly["total_refunds"].round(2)
    monthly["net_revenue"] = monthly["net_revenue"].round(2)

    return monthly


def build_plan_summary(df: pd.DataFrame) -> pd.DataFrame:
    revenue_by_plan = (
        df.groupby("plan_name", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            total_net_revenue=("net_revenue", "sum"),
            total_refunds=("refund_amount", "sum"),
        )
        .sort_values("total_net_revenue", ascending=False)
    )

    plan_customer_ltv = (
        df.groupby(["plan_name", "customer_id"], as_index=False)["net_revenue"]
        .sum()
        .rename(columns={"net_revenue": "customer_lifetime_value"})
    )

    avg_ltv = (
        plan_customer_ltv.groupby("plan_name", as_index=False)
        .agg(avg_customer_lifetime_value=("customer_lifetime_value", "mean"))
    )

    summary = revenue_by_plan.merge(avg_ltv, on="plan_name", how="left")
    summary["total_net_revenue"] = summary["total_net_revenue"].round(2)
    summary["total_refunds"] = summary["total_refunds"].round(2)
    summary["avg_customer_lifetime_value"] = summary["avg_customer_lifetime_value"].round(2)

    return summary


def build_channel_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("acquisition_channel", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            total_net_revenue=("net_revenue", "sum"),
            avg_monthly_revenue_per_customer=("net_revenue", "mean"),
        )
        .sort_values("total_net_revenue", ascending=False)
    )

    summary["total_net_revenue"] = summary["total_net_revenue"].round(2)
    summary["avg_monthly_revenue_per_customer"] = summary[
        "avg_monthly_revenue_per_customer"
    ].round(2)

    return summary


def build_country_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("country", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            total_net_revenue=("net_revenue", "sum"),
            avg_monthly_revenue_per_customer=("net_revenue", "mean"),
        )
        .sort_values("total_net_revenue", ascending=False)
    )

    summary["total_net_revenue"] = summary["total_net_revenue"].round(2)
    summary["avg_monthly_revenue_per_customer"] = summary[
        "avg_monthly_revenue_per_customer"
    ].round(2)

    return summary


def build_display_table(
    df: pd.DataFrame,
    currency_cols: list[str] | None = None,
    pct_cols: list[str] | None = None,
) -> pd.DataFrame:
    display_df = df.copy()

    currency_cols = currency_cols or []
    pct_cols = pct_cols or []

    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(format_currency)

    for col in pct_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda x: f"{x:.2f}%")

    return display_df


st.set_page_config(
    page_title="Customer Retention & Revenue Analytics Warehouse",
    layout="wide",
)

st.title("Customer Retention & Revenue Analytics Warehouse")
st.write(
    "A subscription analytics dashboard built with SQLite, SQL, Python, and Streamlit."
)

if not DB_PATH.exists():
    st.error("Database file not found. Build the database before running the dashboard.")
    st.stop()

base_df = load_base_data()

if base_df.empty:
    st.error("No data was found in the analytics tables.")
    st.stop()

st.sidebar.header("Filters")

plan_options = sorted(base_df["plan_name"].dropna().unique().tolist())
country_options = sorted(base_df["country"].dropna().unique().tolist())
channel_options = sorted(base_df["acquisition_channel"].dropna().unique().tolist())
month_options = sorted(base_df["status_month"].dropna().unique().tolist())

selected_plans = st.sidebar.multiselect(
    "Plan",
    options=plan_options,
    default=plan_options,
)

selected_countries = st.sidebar.multiselect(
    "Country",
    options=country_options,
    default=country_options,
)

selected_channels = st.sidebar.multiselect(
    "Acquisition Channel",
    options=channel_options,
    default=channel_options,
)

selected_month_range = st.sidebar.select_slider(
    "Month Range",
    options=month_options,
    value=(month_options[0], month_options[-1]),
)

filtered_df = base_df[
    base_df["plan_name"].isin(selected_plans)
    & base_df["country"].isin(selected_countries)
    & base_df["acquisition_channel"].isin(selected_channels)
    & (base_df["status_month"] >= selected_month_range[0])
    & (base_df["status_month"] <= selected_month_range[1])
].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

monthly_df = build_monthly_metrics(filtered_df)
plan_summary_df = build_plan_summary(filtered_df)
channel_summary_df = build_channel_summary(filtered_df)
country_summary_df = build_country_summary(filtered_df)

total_customers = filtered_df["customer_id"].nunique()
total_net_revenue = filtered_df["net_revenue"].sum()
avg_monthly_net_revenue = monthly_df["net_revenue"].mean()
avg_monthly_churn = monthly_df["churn_rate_pct"].mean()

customer_ltv_df = (
    filtered_df.groupby("customer_id", as_index=False)["net_revenue"]
    .sum()
    .rename(columns={"net_revenue": "customer_lifetime_value"})
)
avg_customer_lifetime_value = customer_ltv_df["customer_lifetime_value"].mean()

st.caption(
    f"Filtered view: {selected_month_range[0]} to {selected_month_range[1]} | "
    f"{len(selected_plans)} plan(s) | {len(selected_countries)} countr(y/ies) | "
    f"{len(selected_channels)} acquisition channel(s)"
)

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric("Total Customers", f"{total_customers:,}")
metric_2.metric("Total Net Revenue", format_currency(total_net_revenue))
metric_3.metric("Average Monthly Net Revenue", format_currency(avg_monthly_net_revenue))
metric_4.metric("Average Monthly Churn Rate", f"{avg_monthly_churn:.2f}%")
metric_5.metric(
    "Average Customer Lifetime Value",
    format_currency(avg_customer_lifetime_value),
)

st.subheader("Revenue Trend")
revenue_chart_df = monthly_df[["status_month", "gross_revenue", "net_revenue"]].copy()
revenue_chart_df = revenue_chart_df.set_index("status_month")
st.line_chart(revenue_chart_df, use_container_width=True)

st.subheader("Monthly Churn Trend")
churn_chart_df = monthly_df[["status_month", "churn_rate_pct"]].copy()
churn_chart_df = churn_chart_df.set_index("status_month")
st.line_chart(churn_chart_df, use_container_width=True)

chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    st.subheader("Revenue by Plan")
    revenue_by_plan_chart = plan_summary_df[["plan_name", "total_net_revenue"]].copy()
    revenue_by_plan_chart = revenue_by_plan_chart.set_index("plan_name")
    st.bar_chart(revenue_by_plan_chart, use_container_width=True)

with chart_col_2:
    st.subheader("Average Customer Lifetime Value by Plan")
    ltv_by_plan_chart = plan_summary_df[["plan_name", "avg_customer_lifetime_value"]].copy()
    ltv_by_plan_chart = ltv_by_plan_chart.set_index("plan_name")
    st.bar_chart(ltv_by_plan_chart, use_container_width=True)

segment_col_1, segment_col_2 = st.columns(2)

with segment_col_1:
    st.subheader("Revenue by Acquisition Channel")
    channel_chart_df = channel_summary_df[["acquisition_channel", "total_net_revenue"]].copy()
    channel_chart_df = channel_chart_df.set_index("acquisition_channel")
    st.bar_chart(channel_chart_df, use_container_width=True)

with segment_col_2:
    st.subheader("Revenue by Country")
    country_chart_df = country_summary_df[["country", "total_net_revenue"]].copy()
    country_chart_df = country_chart_df.set_index("country")
    st.bar_chart(country_chart_df, use_container_width=True)

st.subheader("Insights")

data_driven_insights: list[str] = []
model_driven_insights: list[str] = []

if not plan_summary_df.empty:
    top_revenue_plan = plan_summary_df.iloc[0]
    data_driven_insights.append(
        f"{top_revenue_plan['plan_name']} is the top revenue-generating plan, "
        f"contributing {format_currency(top_revenue_plan['total_net_revenue'])} "
        f"from {int(top_revenue_plan['customers'])} customers."
    )

if not plan_summary_df.empty:
    top_ltv_plan = plan_summary_df.sort_values(
        "avg_customer_lifetime_value", ascending=False
    ).iloc[0]
    data_driven_insights.append(
        f"{top_ltv_plan['plan_name']} has the highest average customer lifetime value at "
        f"{format_currency(top_ltv_plan['avg_customer_lifetime_value'])}."
    )

if not monthly_df.empty:
    peak_churn_row = monthly_df.sort_values("churn_rate_pct", ascending=False).iloc[0]
    data_driven_insights.append(
        f"Churn peaked in {peak_churn_row['status_month']} at "
        f"{peak_churn_row['churn_rate_pct']:.2f}%, with "
        f"{int(peak_churn_row['cancelled_customers'])} cancellation(s) from "
        f"{int(peak_churn_row['active_customers'])} active customers."
    )

if not monthly_df.empty:
    best_revenue_month = monthly_df.sort_values("net_revenue", ascending=False).iloc[0]
    data_driven_insights.append(
        f"The strongest month for net revenue was {best_revenue_month['status_month']}, "
        f"reaching {format_currency(best_revenue_month['net_revenue'])}."
    )

if not channel_summary_df.empty:
    top_channel = channel_summary_df.iloc[0]
    model_driven_insights.append(
        f"A retention model would likely prioritize customers acquired through "
        f"{top_channel['acquisition_channel']}, because this channel currently carries "
        f"the largest revenue base."
    )

if not plan_summary_df.empty:
    premium_candidate = plan_summary_df.sort_values(
        "avg_customer_lifetime_value", ascending=False
    ).iloc[0]
    model_driven_insights.append(
        f"{premium_candidate['plan_name']} is the strongest candidate for proactive "
        f"retention scoring because it combines high per-customer value with meaningful "
        f"revenue exposure."
    )

if not monthly_df.empty:
    model_driven_insights.append(
        "A next predictive layer could forecast monthly churn using recent cancellation "
        "patterns, payment outcomes, and plan mix to flag higher-risk periods earlier."
    )

st.markdown("**Data-driven insights**")
for insight in data_driven_insights:
    st.write(f"- {insight}")

st.markdown("**Model-driven insights**")
for insight in model_driven_insights:
    st.write(f"- {insight}")

st.subheader("Detailed Tables")

tab_1, tab_2, tab_3, tab_4, tab_5 = st.tabs(
    [
        "Monthly Performance",
        "Plan Performance",
        "Channel Performance",
        "Country Performance",
        "Filtered Records",
    ]
)

with tab_1:
    monthly_display_df = build_display_table(
        monthly_df,
        currency_cols=["gross_revenue", "total_refunds", "net_revenue", "arppu"],
        pct_cols=["churn_rate_pct"],
    )
    st.dataframe(monthly_display_df, use_container_width=True)

with tab_2:
    plan_display_df = build_display_table(
        plan_summary_df,
        currency_cols=["total_net_revenue", "total_refunds", "avg_customer_lifetime_value"],
    )
    st.dataframe(plan_display_df, use_container_width=True)

with tab_3:
    channel_display_df = build_display_table(
        channel_summary_df,
        currency_cols=["total_net_revenue", "avg_monthly_revenue_per_customer"],
    )
    st.dataframe(channel_display_df, use_container_width=True)

with tab_4:
    country_display_df = build_display_table(
        country_summary_df,
        currency_cols=["total_net_revenue", "avg_monthly_revenue_per_customer"],
    )
    st.dataframe(country_display_df, use_container_width=True)

with tab_5:
    record_columns = [
        "status_month",
        "customer_id",
        "full_name",
        "country",
        "acquisition_channel",
        "plan_name",
        "invoice_id",
        "invoice_status",
        "payment_status",
        "amount_due",
        "amount_paid",
        "refund_amount",
        "net_revenue",
        "is_cancelled_in_month",
    ]
    records_display_df = build_display_table(
        filtered_df[record_columns].copy(),
        currency_cols=["amount_due", "amount_paid", "refund_amount", "net_revenue"],
    )
    st.dataframe(records_display_df, use_container_width=True)