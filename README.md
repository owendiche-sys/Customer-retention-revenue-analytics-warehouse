# Customer Retention \& Revenue Analytics Warehouse

An end-to-end subscription analytics project built with **SQLite, SQL, Python, pandas, and Streamlit** to model customer retention, churn, revenue performance, and customer lifetime value through a warehouse-style analytics workflow.

## Overview

This project simulates a real-world analytics engineering and business intelligence workflow for a subscription business. It starts with raw customer and billing data, loads the data into a **SQLite warehouse**, transforms the data into clean **staging** and **mart** layers, calculates business KPIs, and presents the final outputs in an interactive **Streamlit dashboard**.

The goal of the project is to show how raw operational data can be turned into decision-ready analytics for stakeholders interested in retention, revenue growth, plan performance, and customer value.

## Business Problem

Subscription businesses need clear visibility into:

* revenue trends over time
* active customers and churn behaviour
* plan-level revenue contribution
* customer lifetime value by plan
* acquisition channel performance
* country-level revenue distribution

Without a structured analytics layer, it becomes difficult to produce consistent reporting or understand which customer segments are most valuable.

## Project Objectives

This project was built to:

* design a lightweight analytics warehouse using SQLite
* load and manage multi-table subscription business data
* clean and standardise raw data into staging tables
* create mart tables for reporting and dashboarding
* calculate core retention and revenue KPIs
* build an interactive dashboard for business users
* demonstrate end-to-end analytics engineering workflow for a portfolio project

## Tech Stack

* **SQLite** for the analytics database
* **SQL** for schema creation, transformations, and KPI logic
* **Python** for automation and pipeline scripts
* **pandas** for CSV loading and query handling
* **Streamlit** for the dashboard interface

## Warehouse Architecture

The project follows a warehouse-style layered structure:

### Raw Layer

The raw layer stores source-level data loaded directly from CSV files.

Tables:

* `raw\_customers`
* `raw\_subscriptions`
* `raw\_invoices`
* `raw\_payments`
* `raw\_refunds`

### Staging Layer

The staging layer standardises and cleans the raw data for downstream analysis.

Tables:

* `stg\_customers`
* `stg\_subscriptions`
* `stg\_invoices`
* `stg\_payments`
* `stg\_refunds`

### Mart Layer

The mart layer contains analytics-ready dimension and fact tables.

Tables:

* `dim\_customer`
* `dim\_plan`
* `fct\_revenue\_monthly`
* `fct\_customer\_monthly\_status`

## Data Model Summary

### `dim\_customer`

Contains customer-level descriptive attributes such as:

* customer ID
* name
* email
* signup date
* country
* acquisition channel

### `dim\_plan`

Contains subscription plan attributes such as:

* plan name
* billing cycle
* monthly price

### `fct\_revenue\_monthly`

Monthly revenue summary table used for revenue trend analysis, including:

* paying customers
* gross revenue
* total refunds
* net revenue

### `fct\_customer\_monthly\_status`

Monthly customer-plan status table used for retention and churn analysis, including:

* customer and subscription identifiers
* plan details
* invoice and payment status
* revenue amounts
* cancellation flags
* active-month indicators

## Key KPIs

The project calculates and surfaces the following metrics:

* Total Customers
* Total Net Revenue
* Average Monthly Net Revenue
* Average Monthly Churn Rate
* Gross Revenue by Month
* Net Revenue by Month
* Revenue by Plan
* Average Customer Lifetime Value by Plan
* Revenue by Acquisition Channel
* Revenue by Country

## Dashboard Features

The Streamlit dashboard includes:

* KPI summary cards
* monthly revenue trend chart
* monthly churn trend chart
* revenue by plan chart
* average customer lifetime value by plan chart
* revenue by acquisition channel chart
* revenue by country chart
* detailed performance tables
* business insight summaries

### Interactive Filters

The dashboard supports filtering by:

* subscription plan
* country
* acquisition channel
* month range

## Project Structure

```text
customer-retention-revenue-analytics-warehouse/
│
├── data/
│   └── raw/
│       ├── customers.csv
│       ├── subscriptions.csv
│       ├── invoices.csv
│       ├── payments.csv
│       └── refunds.csv
│
├── database/
│   └── customer\_analytics.db
│
├── sql/
│   ├── schema.sql
│   ├── staging.sql
│   ├── marts.sql
│   └── kpi\_queries.sql
│
├── scripts/
│   ├── build\_database.py
│   ├── generate\_sample\_data.py
│   ├── load\_csvs.py
│   ├── run\_staging.py
│   ├── run\_marts.py
│   ├── check\_database.py
│   └── run\_kpis.py
│
├── dashboard/
│   └── app.py
│
│
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1\. Clone the repository

```bash
git clone <your-repo-url>
cd customer-retention-revenue-analytics-warehouse
```

### 2\. Create and activate a virtual environment

**Windows**

```bash
python -m venv .venv
.venv\\\\Scripts\\\\activate
```

### 3\. Install dependencies

```bash
pip install -r requirements.txt
```

## How to Run the Project

Run the pipeline in this order:

### 1\. Build the database schema

```bash
python scripts/build\\\_database.py
```

### 2\. Generate the sample source data

```bash
python scripts/generate\\\_sample\\\_data.py
```

### 3\. Load CSV data into the raw tables

```bash
python scripts/load\\\_csvs.py
```

### 4\. Create the staging layer

```bash
python scripts/run\\\_staging.py
```

### 5\. Create the mart layer

```bash
python scripts/run\\\_marts.py
```

### 6\. Validate table counts and sample outputs

```bash
python scripts/check\\\_database.py
```

### 7\. Run KPI outputs in the terminal

```bash
python scripts/run\\\_kpis.py
```

### 8\. Launch the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

## Example Business Findings

Using the generated sample data, the dashboard highlighted insights such as:

* revenue generally increased across the analysis window
* Pro generated the highest total revenue
* Premium produced the highest average customer lifetime value
* churn was present but varied by month
* customer value differed across plans, channels, and geographies

## Why This Project Is Valuable

This project demonstrates more than dashboard building. It shows how to:

* structure an analytics warehouse
* work with multiple related business tables
* write reusable SQL transformations
* move from raw data to reporting-ready marts
* build business metrics from a customer and subscription dataset
* connect a relational warehouse to an interactive front end

It is especially useful as a portfolio project for roles related to:

* data analytics
* business intelligence
* analytics engineering
* product analytics
* operations analytics
* junior data engineering

## Future Improvements

Possible extensions for future versions include:

* cohort retention analysis
* customer segmentation by tenure or behaviour
* predictive churn modelling
* revenue forecasting
* automated data quality checks
* dashboard styling upgrades
* deployment to Streamlit Community Cloud

## Author

**Owen Nda Diche**

