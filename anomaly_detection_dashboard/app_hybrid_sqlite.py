from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Hybrid SQLite Dashboard",
    layout="wide",
)

st.title("Hybrid Network Anomaly Detection Dashboard")

st.info(
    "Alert records are loaded from the local SQLite database."
)

DATABASE_FILE = Path(__file__).parent / "alerts.db"
TABLE_NAME = "hybrid_alerts"


@st.cache_data
def load_results(database_path):
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(
            f"SELECT * FROM {TABLE_NAME}",
            connection,
        )


if not DATABASE_FILE.exists():
    st.error(f"SQLite database not found: {DATABASE_FILE}")
    st.stop()

try:
    alerts = load_results(DATABASE_FILE)
except Exception as error:
    st.error(f"Could not load alerts from SQLite: {error}")
    st.stop()


required_columns = {
    "record_id",
    "actual_class",
    "if_score",
    "if_score_normalized",
    "if_prediction_1pct",
    "if_status_1pct",
    "ae_score",
    "ae_score_normalized",
    "ae_prediction_1pct",
    "ae_status_1pct",
    "if_ae_agreement",
    "hybrid_score",
    "hybrid_prediction_0.5pct",
    "hybrid_prediction_1pct",
    "hybrid_prediction_3pct",
    "default_threshold",
    "default_prediction",
    "default_status",
    "correct_prediction",
}

missing_columns = required_columns - set(alerts.columns)

if missing_columns:
    st.error(
        "Required columns are missing: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()


# Severity is based on the three false-positive-budget thresholds.
alerts["severity"] = "Low"
alerts.loc[
    alerts["hybrid_prediction_3pct"] == 1,
    "severity",
] = "Medium"
alerts.loc[
    alerts["hybrid_prediction_1pct"] == 1,
    "severity",
] = "High"
alerts.loc[
    alerts["hybrid_prediction_0.5pct"] == 1,
    "severity",
] = "Critical"


st.sidebar.header("Alert Filters")

selected_status = st.sidebar.selectbox(
    "Detection status",
    ["All", "Anomaly", "Normal"],
)

selected_severities = st.sidebar.multiselect(
    "Severity",
    ["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium", "Low"],
)

agreement_options = [
    "All",
    "Both anomaly",
    "IF only",
    "AE only",
    "Neither",
]

selected_agreement = st.sidebar.selectbox(
    "Model agreement",
    agreement_options,
)


filtered_alerts = alerts.copy()

if selected_status != "All":
    filtered_alerts = filtered_alerts[
        filtered_alerts["default_status"] == selected_status
    ]

filtered_alerts = filtered_alerts[
    filtered_alerts["severity"].isin(selected_severities)
]

if selected_agreement != "All":
    filtered_alerts = filtered_alerts[
        filtered_alerts["if_ae_agreement"] == selected_agreement
    ]


total_records = len(alerts)
total_anomalies = int(alerts["default_prediction"].sum())
total_normal = total_records - total_anomalies
default_threshold = alerts["default_threshold"].iloc[0]

agreement_rate = (
    alerts["if_prediction_1pct"]
    == alerts["ae_prediction_1pct"]
).mean() * 100


column1, column2, column3, column4, column5 = st.columns(5)

column1.metric("Total Records", f"{total_records:,}")
column2.metric("Hybrid Anomalies", f"{total_anomalies:,}")
column3.metric("Hybrid Normal", f"{total_normal:,}")
column4.metric("Hybrid Threshold", f"{default_threshold:.6f}")
column5.metric("IF–AE Agreement", f"{agreement_rate:.2f}%")


st.subheader("Hybrid Detection Results")

display_columns = [
    "record_id",
    "if_score",
    "ae_score",
    "hybrid_score",
    "if_ae_agreement",
    "default_status",
    "severity",
    "actual_class",
    "correct_prediction",
]

st.dataframe(
    filtered_alerts[display_columns].head(1000),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    f"Filtered records: {len(filtered_alerts):,}. "
    "The table displays the first 1,000 records."
)


if filtered_alerts.empty:
    st.warning("No records match the selected filters.")
    st.stop()


st.subheader("Selected Record Details")

selected_record_id = st.selectbox(
    "Select a record",
    filtered_alerts["record_id"].tolist(),
)

selected_record = filtered_alerts[
    filtered_alerts["record_id"] == selected_record_id
].iloc[0]


detail1, detail2, detail3, detail4 = st.columns(4)

detail1.metric("Record ID", int(selected_record["record_id"]))
detail2.metric("IF Score", f"{selected_record['if_score']:.6f}")
detail3.metric("AE Score", f"{selected_record['ae_score']:.6f}")
detail4.metric(
    "Hybrid Score",
    f"{selected_record['hybrid_score']:.6f}",
)


result1, result2, result3, result4 = st.columns(4)

result1.metric("IF Status", selected_record["if_status_1pct"])
result2.metric("AE Status", selected_record["ae_status_1pct"])
result3.metric("Model Agreement", selected_record["if_ae_agreement"])
result4.metric("Final Status", selected_record["default_status"])


st.write(f"**Severity:** {selected_record['severity']}")
st.write(
    f"**Hybrid threshold:** "
    f"{selected_record['default_threshold']:.6f}"
)
st.write(
    f"**Actual class (evaluation only):** "
    f"{selected_record['actual_class']}"
)
st.write(
    f"**Correct prediction:** "
    f"{bool(selected_record['correct_prediction'])}"
)


st.subheader("Score Comparison")

score_data = pd.DataFrame(
    {
        "Model": [
            "Isolation Forest (normalised)",
            "Autoencoder (normalised)",
            "Hybrid",
        ],
        "Score": [
            selected_record["if_score_normalized"],
            selected_record["ae_score_normalized"],
            selected_record["hybrid_score"],
        ],
    }
)

st.bar_chart(
    score_data.set_index("Model"),
    horizontal=True,
)


if selected_record["default_prediction"] == 1:
    st.warning(
        f"Explanation: The hybrid score "
        f"({selected_record['hybrid_score']:.6f}) is equal to or above "
        f"the 1% budget threshold "
        f"({selected_record['default_threshold']:.6f}). "
        f"The model-agreement result is "
        f"'{selected_record['if_ae_agreement']}'. "
        f"Isolation Forest classified the record as "
        f"{selected_record['if_status_1pct']}, while the Autoencoder "
        f"classified it as {selected_record['ae_status_1pct']}. "
        "Therefore, the combined system flags this record as anomalous."
    )
else:
    st.success(
        f"Explanation: The hybrid score "
        f"({selected_record['hybrid_score']:.6f}) is below "
        f"the 1% budget threshold "
        f"({selected_record['default_threshold']:.6f}). "
        f"The model-agreement result is "
        f"'{selected_record['if_ae_agreement']}'. "
        f"Isolation Forest classified the record as "
        f"{selected_record['if_status_1pct']}, while the Autoencoder "
        f"classified it as {selected_record['ae_status_1pct']}. "
        "Therefore, the combined system classifies this record as normal."
    )


