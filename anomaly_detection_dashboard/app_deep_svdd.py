from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Deep SVDD Dashboard",
    page_icon="🎯",
    layout="wide",
)


REQUIRED_COLUMNS = {
    "record_id",
    "actual_label",
    "actual_class",
    "deep_svdd_score",
    "deep_svdd_prediction_0.5pct",
    "deep_svdd_prediction_1pct",
    "deep_svdd_prediction_3pct",
    "deep_svdd_status_0.5pct",
    "deep_svdd_status_1pct",
    "deep_svdd_status_3pct",
    "default_threshold",
    "default_prediction",
    "default_status",
    "correct_prediction",
}


def find_default_csv() -> Path | None:
    """Find the Deep SVDD dashboard CSV in common project locations."""
    base = Path(__file__).resolve().parent
    candidates = [
        base / "reports" / "deep_svdd_dashboard_results.csv",
        base / "data" / "model_outputs" / "deep_svdd_dashboard_results.csv",
        base / "data" / "deep_svdd_dashboard_results.csv",
        base / "deep_svdd_dashboard_results.csv",
    ]
    return next((path for path in candidates if path.exists()), None)


@st.cache_data(show_spinner="Loading Deep SVDD results...")
def load_csv(path_or_file) -> pd.DataFrame:
    data = pd.read_csv(path_or_file)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(
            "The CSV is missing required columns: " + ", ".join(sorted(missing))
        )

    numeric_columns = [
        "record_id",
        "actual_label",
        "deep_svdd_score",
        "deep_svdd_prediction_0.5pct",
        "deep_svdd_prediction_1pct",
        "deep_svdd_prediction_3pct",
        "default_threshold",
        "default_prediction",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["correct_prediction"] = (
        data["correct_prediction"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
        .fillna(False)
        .astype(bool)
    )
    return data


def assign_severity(row: pd.Series) -> str:
    """Use the supplied budget decisions to create an explainable priority."""
    if int(row["deep_svdd_prediction_0.5pct"]) == 1:
        return "Critical"
    if int(row["deep_svdd_prediction_1pct"]) == 1:
        return "High"
    if int(row["deep_svdd_prediction_3pct"]) == 1:
        return "Medium"
    return "Low"


def build_explanation(row: pd.Series) -> str:
    score = float(row["deep_svdd_score"])
    threshold = float(row["default_threshold"])
    status = str(row["default_status"])
    severity = str(row["severity"])
    comparison = "equal to or above" if score >= threshold else "below"

    if status == "Anomaly":
        result_text = (
            "The record is flagged for analyst investigation because its Deep "
            "SVDD distance score crossed the default threshold."
        )
    else:
        result_text = (
            "The record is shown as normal at the default operating point because "
            "its Deep SVDD distance score did not cross the threshold."
        )

    return (
        f"The Deep SVDD anomaly score is {score:.8f}, which is {comparison} the "
        f"default 1% threshold of {threshold:.8f}. Therefore, the model status "
        f"is {status} and the dashboard priority is {severity}. {result_text} "
        "An anomaly is not automatically a confirmed cyberattack."
    )


st.title("🎯 Deep SVDD Network Anomaly Dashboard")
st.caption(
    "Offline UNSW-NB15 evaluation • Default operating point: 1% false-positive budget"
)

default_csv = find_default_csv()
uploaded_file = None

with st.sidebar:
    st.header("Deep SVDD model information")
    st.info(
        "Deep SVDD learns a compact representation of normal traffic. The score "
        "measures a record's distance from the learned normal centre; in the "
        "supplied output, a higher score means more anomalous."
    )
    st.caption(
        "Severity uses the model's supplied budget decisions: Critical crosses "
        "the strict 0.5% decision, High crosses 1%, Medium crosses 3%, and Low "
        "crosses none."
    )

    if default_csv is None:
        st.subheader("Load results")
        uploaded_file = st.file_uploader(
            "Choose deep_svdd_dashboard_results.csv",
            type="csv",
        )

data_source = default_csv if default_csv is not None else uploaded_file

if data_source is None:
    st.warning(
        "Place `deep_svdd_dashboard_results.csv` in the `reports`, "
        "`data/model_outputs`, `data`, or project root folder. You can also upload "
        "the CSV from the sidebar."
    )
    st.stop()

try:
    df = load_csv(data_source)
except Exception as exc:
    st.error(f"Could not load the Deep SVDD results: {exc}")
    st.stop()

df = df.copy()
df["severity"] = df.apply(assign_severity, axis=1)

if default_csv is not None:
    st.success(f"Loaded {len(df):,} Deep SVDD records from `{default_csv.name}`.")
else:
    st.success(f"Loaded {len(df):,} Deep SVDD records from the uploaded CSV.")

total_records = len(df)
anomaly_count = int((df["default_status"] == "Anomaly").sum())
normal_count = int((df["default_status"] == "Normal").sum())
default_threshold = float(df["default_threshold"].dropna().iloc[0])
accuracy = (
    float((df["default_prediction"] == df["actual_label"]).mean())
    if total_records
    else 0.0
)

metric_columns = st.columns(5)
metric_columns[0].metric("Total records", f"{total_records:,}")
metric_columns[1].metric("Anomalies", f"{anomaly_count:,}")
metric_columns[2].metric("Normal", f"{normal_count:,}")
metric_columns[3].metric("Default threshold", f"{default_threshold:.8f}")
metric_columns[4].metric("Offline accuracy", f"{accuracy:.2%}")

st.divider()
st.subheader("Alert filters")
filter_columns = st.columns([1, 1, 1, 1.2])

status_options = filter_columns[0].multiselect(
    "Detection status",
    ["Anomaly", "Normal"],
    default=["Anomaly", "Normal"],
)
severity_options = filter_columns[1].multiselect(
    "Severity",
    ["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium", "Low"],
)
class_options = filter_columns[2].multiselect(
    "Actual class (evaluation only)",
    ["Attack", "Normal"],
    default=["Attack", "Normal"],
)
record_search = filter_columns[3].text_input(
    "Record ID",
    placeholder="Enter an exact ID",
)

filtered = df[
    df["default_status"].isin(status_options)
    & df["severity"].isin(severity_options)
    & df["actual_class"].isin(class_options)
].copy()

if record_search.strip():
    try:
        record_id = int(record_search.strip())
        filtered = filtered[filtered["record_id"] == record_id]
    except ValueError:
        st.warning("Record ID must be a whole number.")
        filtered = filtered.iloc[0:0]

st.subheader(f"Model results ({len(filtered):,} records)")

display_columns = [
    "record_id",
    "deep_svdd_score",
    "default_status",
    "severity",
    "actual_class",
    "correct_prediction",
]
display_table = filtered[display_columns].rename(
    columns={
        "record_id": "Record ID",
        "deep_svdd_score": "Deep SVDD score",
        "default_status": "Detection status",
        "severity": "Severity",
        "actual_class": "Actual class",
        "correct_prediction": "Correct prediction",
    }
)

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True,
    height=360,
    column_config={
        "Deep SVDD score": st.column_config.NumberColumn(format="%.8f"),
        "Correct prediction": st.column_config.CheckboxColumn(),
    },
)

if filtered.empty:
    st.info("No records match the selected filters.")
    st.stop()

st.divider()
st.subheader("Selected record details")

record_ids = filtered["record_id"].astype(int).tolist()
selected_record_id = st.selectbox(
    "Select a record",
    record_ids,
    format_func=lambda value: f"Record {value}",
)
selected_row = filtered.loc[filtered["record_id"] == selected_record_id].iloc[0]

detail_columns = st.columns(6)
detail_columns[0].metric("Record ID", f"{int(selected_row['record_id']):,}")
detail_columns[1].metric("Deep SVDD score", f"{selected_row['deep_svdd_score']:.8f}")
detail_columns[2].metric("Threshold", f"{selected_row['default_threshold']:.8f}")
detail_columns[3].metric("Status", selected_row["default_status"])
detail_columns[4].metric("Severity", selected_row["severity"])
detail_columns[5].metric("Actual class", selected_row["actual_class"])

st.markdown("#### Alert explanation")
explanation = build_explanation(selected_row)
if selected_row["default_status"] == "Anomaly":
    st.warning(explanation)
else:
    st.info(explanation)

with st.expander("Compare all false-positive budgets"):
    comparison = pd.DataFrame(
        {
            "Operating point": ["0.5% budget", "1% budget (default)", "3% budget"],
            "Record prediction": [
                int(selected_row["deep_svdd_prediction_0.5pct"]),
                int(selected_row["deep_svdd_prediction_1pct"]),
                int(selected_row["deep_svdd_prediction_3pct"]),
            ],
            "Record status": [
                selected_row["deep_svdd_status_0.5pct"],
                selected_row["deep_svdd_status_1pct"],
                selected_row["deep_svdd_status_3pct"],
            ],
        }
    )
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.caption(
        "Prediction 1 means anomaly and prediction 0 means normal at the "
        "corresponding operating point."
    )

st.caption(
    "Actual class and correctness are included only for offline evaluation; "
    "they are not used to generate the Deep SVDD prediction."
)
