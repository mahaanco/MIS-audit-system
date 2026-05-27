# MIS Variance Analysis 

## Overview

This is a production-grade AI-powered MIS variance analysis and audit automation system built using Python, Streamlit, Pandas, and Plotly.

The system dynamically processes MIS files from multiple formats and automatically performs rolling month-on-month variance analysis, high variance detection, AI query prioritization, and interactive dashboard visualization.

The application is designed for:
- Chartered Accountants
- Audit Firms
- CFO Offices
- Finance Teams
- Internal Auditors
- MIS Analysts

---

# Features

## Universal MIS File Reader

Supports:
- `.xlsx`
- `.xls`
- `.xlsb`
- `.csv`
- `.txt`
- `.ods`

Handles:
- merged cells
- blank rows
- duplicate headers
- formatting inconsistencies
- subtotal rows
- narration rows
- multiple MIS structures

---

# Dynamic MIS Structure Handling

Automatically detects:
- Ledger column
- Month columns
- Debit/Credit structures
- Net amount structures

Supports formats like:

### Single Amount Format

| GL | Jan |
|---|---|

### Debit / Credit Format

| GL | Debit | Credit |
|---|---|---|

### Multi-Month DR/CR Format

| GL | Jan DR | Jan CR | Feb DR | Feb CR |
|---|---|---|---|---|

The system automatically converts:

```text
Net Amount = Debit - Credit
```

---

# Rolling Variance Analysis

Automatically calculates:

- Previous Month
- Current Month
- Variance Amount
- Variance %
- Variance Status

Example:

```text
Mar vs Feb
Feb vs Jan
Jan vs Dec
```

No yearly aggregation is performed.

---

# Dynamic Period Selection

Users can select:
- Start Month
- End Month

Example:
- Apr 2024 → Mar 2025
- Jan 2025 → Jun 2025

The system only performs variance analysis for the selected period.

---

# High Variance Detection

Accounts are classified into:
- High Variance
- Normal

Based on configurable threshold percentage.

---

# AI Query Prioritization

Automatically generates audit/client queries such as:

```text
Why did Advertisement Expense increase by 120%?
```

Queries are prioritized as:
- Critical
- High
- Medium
- Low

Based on:
- variance %
- materiality
- risk indicators

---

# Interactive Dashboard

Includes:
- Variance tables
- Top variance charts
- Variance % charts
- High variance filtering
- Dynamic period analysis

Built using Plotly interactive visualizations.

---

# Error Handling

Includes:
- empty dataframe protection
- invalid row filtering
- duplicate header handling
- dynamic column normalization
- unsupported format validation
- safe numeric conversion

---

# Project Structure

```text
project/
│
├── app.py
├── utils.py
├── variance_analysis.py
├── queries.py
├── requirements.txt
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd <project-folder>
```

---

# Create Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Application

```bash
streamlit run app.py
```

---

# Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

---

# Key Capabilities

- Dynamic MIS parsing
- Multi-format support
- Rolling variance analysis
- AI-driven query generation
- Debit/Credit normalization
- Interactive dashboards
- Period-based analysis
- Audit-focused analytics

---

# Future Enhancements

Planned improvements:
- AI root cause analysis
- OCR-based PDF MIS reading
- PowerPoint audit report generation
- Financial ratio analysis
- Audit working paper export
- Risk scoring engine
- Multi-client workspace
- Database integration
- OpenAI-powered commentary engine
- Predictive analytics
- Fraud detection

---

# Use Cases

- Statutory Audit
- Internal Audit
- MIS Review
- Financial Analytics
- Variance Investigation
- CFO Reporting
- Due Diligence
- Budget vs Actual Analysis

---

# Deployment

The application is fully deployable on:
- Streamlit Cloud
- AWS
- Azure
- Docker
- Local Servers

---

# License

This project is intended for internal audit automation and financial analytics purposes.
