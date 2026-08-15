# Network Anomaly Detection Dashboard

## Overview

This Streamlit dashboard presents the outputs of an explainable, false-positive-aware hybrid network anomaly detection system. It displays Isolation Forest, Autoencoder and combined Hybrid results with threshold-based severity, model agreement, filtering and record-level explanations.

## Dashboard Files

* `app_mock.py` — Initial dashboard using synthetic mock alerts.
* `app_isolation_forest.py` — Isolation Forest results, threshold decisions and explanations.
* `app_autoencoder.py` — Autoencoder reconstruction errors and top abnormal features.
* `app_hybrid.py` — Combined Isolation Forest and Autoencoder results.
* `app_hybrid_sqlite.py` — Final Hybrid dashboard loading alert records from SQLite.
* `database.py` — Creates the SQLite database from the Hybrid model-output CSV.
* `alerts.db` — Local SQLite database containing the `hybrid_alerts` table.

## Model-Output Files

The `data/model_outputs` folder contains:

* `isolation_forest_dashboard_results.csv`
* `autoencoder_dashboard_results.csv`
* `hybrid_results_for_dashboard.csv`

The Hybrid results include Isolation Forest scores, Autoencoder scores, model statuses, model agreement, Hybrid scores, threshold decisions and evaluation results.

## Installation

Create and activate a Python virtual environment, then install the required packages:

```cmd
pip install streamlit pandas
```

SQLite support is included with Python.

## Create the SQLite Database

Run:

```cmd
.\.venv\Scripts\python.exe database.py
```

This creates:

* Database: `alerts.db`
* Table: `hybrid_alerts`
* Stored records: 82,332

## Run the Dashboards

Isolation Forest:

```cmd
.\.venv\Scripts\python.exe -m streamlit run app_isolation_forest.py
```

Autoencoder:

```cmd
.\.venv\Scripts\python.exe -m streamlit run app_autoencoder.py
```

Hybrid CSV version:

```cmd
.\.venv\Scripts\python.exe -m streamlit run app_hybrid.py
```

Hybrid SQLite version:

```cmd
.\.venv\Scripts\python.exe -m streamlit run app_hybrid_sqlite.py
```

## Dashboard Features

* Detection-status filtering
* Severity filtering
* Model-agreement filtering
* Isolation Forest score display
* Autoencoder reconstruction-error display
* Hybrid anomaly score
* False-positive-budget threshold
* Severity logic
* IF-only, AE-only, both-anomaly and neither classifications
* Selected-record details
* Record-level alert explanations
* SQLite alert storage and retrieval
* Missing-file and missing-column error handling

## SQLite Design

The final dashboard uses one integrated `hybrid_alerts` table. It does not store only the Hybrid result. Each record also contains the Isolation Forest score and status, Autoencoder score and status, model agreement and final Hybrid decision. This avoids unnecessary duplication across separate databases.

## Current Hybrid Summary

* Total records: 82,332
* Hybrid anomalies: 30,059
* Hybrid normal records: 52,273
* IF–AE agreement: 96.83%
* Default 1% budget threshold: 0.980082


