from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Autoencoder Dashboard",
    layout="wide",
)

st.title("Autoencoder Anomaly Detection Dashboard")

data_file = (
    Path(__file__).parent
    / "data"
    / "model_outputs"
    / "autoencoder_dashboard_results.csv"
)


@st.cache_data
def load_results(file_path):
    return pd.read_csv(file_path)


if not data_file.exists():
    st.error(f"Model-output file not found: {data_file}")
    st.stop()

try:
    alerts = load_results(data_file)
except Exception as error:
    st.error(f"Could not load the model-output file: {error}")
    st.stop()


required_columns = {
    "record_id",
    "actual_class",
    "ae_score",
    "ae_prediction_0.5pct",
    "ae_prediction_1pct",
    "ae_prediction_3pct",
    "default_threshold",
    "default_prediction",
    "default_status",
    "correct_prediction",
    "top_feature_1",
    "top_feature_1_error",
    "top_feature_2",
    "top_feature_2_error",
    "top_feature_3",
    "top_feature_3_error",
}

missing_columns = required_columns - set(alerts.columns)

if missing_columns:
    st.error(
        "Required columns are missing: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()


alerts["severity"] = "Low"
alerts.loc[alerts["ae_prediction_3pct"] == 1, "severity"] = "Medium"
alerts.loc[alerts["ae_prediction_1pct"] == 1, "severity"] = "High"
alerts.loc[alerts["ae_prediction_0.5pct"] == 1, "severity"] = "Critical"


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


filtered_alerts = alerts.copy()

if selected_status != "All":
    filtered_alerts = filtered_alerts[
        filtered_alerts["default_status"] == selected_status
    ]

filtered_alerts = filtered_alerts[
    filtered_alerts["severity"].isin(selected_severities)
]


total_records = len(alerts)
total_anomalies = int(alerts["default_prediction"].sum())
total_normal = total_records - total_anomalies
default_threshold = alerts["default_threshold"].iloc[0]

column1, column2, column3, column4 = st.columns(4)

column1.metric("Total Records", f"{total_records:,}")
column2.metric("Detected Anomalies", f"{total_anomalies:,}")
column3.metric("Detected Normal", f"{total_normal:,}")
column4.metric("Default AE Threshold", f"{default_threshold:.6f}")


st.subheader("Autoencoder Results")

display_columns = [
    "record_id",
    "ae_score",
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
detail2.metric("AE Score", f"{selected_record['ae_score']:.6f}")
detail3.metric(
    "Threshold",
    f"{selected_record['default_threshold']:.6f}",
)
detail4.metric("Status", selected_record["default_status"])

st.write(f"**Severity:** {selected_record['severity']}")
st.write(
    f"**Actual class (evaluation only):** "
    f"{selected_record['actual_class']}"
)
st.write(
    f"**Correct prediction:** "
    f"{selected_record['correct_prediction']}"
)


st.subheader("Top Reconstruction-Error Features")

feature1, feature2, feature3 = st.columns(3)

feature1.metric(
    selected_record["top_feature_1"],
    f"{selected_record['top_feature_1_error']:.6f}",
)
feature2.metric(
    selected_record["top_feature_2"],
    f"{selected_record['top_feature_2_error']:.6f}",
)
feature3.metric(
    selected_record["top_feature_3"],
    f"{selected_record['top_feature_3_error']:.6f}",
)


if selected_record["default_prediction"] == 1:
    st.warning(
        f"Explanation: The Autoencoder reconstruction error "
        f"({selected_record['ae_score']:.6f}) is equal to or above "
        f"the 1% budget threshold "
        f"({selected_record['default_threshold']:.6f}). "
        "Therefore, this record is flagged as anomalous. "
        f"The largest reconstruction errors occurred in "
        f"{selected_record['top_feature_1']}, "
        f"{selected_record['top_feature_2']} and "
        f"{selected_record['top_feature_3']}."
    )
else:
    st.success(
        f"Explanation: The Autoencoder reconstruction error "
        f"({selected_record['ae_score']:.6f}) is below "
        f"the 1% budget threshold "
        f"({selected_record['default_threshold']:.6f}). "
        "Therefore, this record is classified as normal."
    )

