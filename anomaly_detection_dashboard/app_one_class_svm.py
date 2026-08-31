from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="One-Class SVM Dashboard",
    page_icon="🛡️",
    layout="wide",
)


# Thresholds calculated in One_Class_SVM_Model.ipynb from normal validation data.
THRESHOLDS = {
    "0.5% budget": 0.71522502,
    "1% budget (default)": -0.00005331,
    "3% budget": -1.09146021,
}

STATUS_COLUMNS = {
    "0.5% budget": "ocsvm_status_0.5pct",
    "1% budget (default)": "ocsvm_status_1pct",
    "3% budget": "ocsvm_status_3pct",
}

PREDICTION_COLUMNS = {
    "0.5% budget": "ocsvm_prediction_0.5pct",
    "1% budget (default)": "ocsvm_prediction_1pct",
    "3% budget": "ocsvm_prediction_3pct",
}

REQUIRED_COLUMNS = {
    "record_id",
    "actual_label",
    "actual_class",
    "ocsvm_score",
    "ocsvm_prediction_0.5pct",
    "ocsvm_prediction_1pct",
    "ocsvm_prediction_3pct",
    "ocsvm_status_0.5pct",
    "ocsvm_status_1pct",
    "ocsvm_status_3pct",
    "default_threshold",
    "default_prediction",
    "default_status",
    "correct_prediction",
}


def find_default_csv() -> Path | None:
    """Find the dashboard CSV in the common project locations."""
    base = Path(__file__).resolve().parent
    candidates = [
        base / "reports" / "ocsvm_dashboard_results.csv",
        base / "data" / "model_outputs" / "ocsvm_dashboard_results.csv",
        base / "data" / "ocsvm_dashboard_results.csv",
        base / "ocsvm_dashboard_results.csv",
    ]
    return next((path for path in candidates if path.exists()), None)


@st.cache_data(show_spinner="Loading One-Class SVM results...")
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
        "ocsvm_score",
        "ocsvm_prediction_0.5pct",
        "ocsvm_prediction_1pct",
        "ocsvm_prediction_3pct",
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


def assign_severity(score: float) -> str:
    """Map score strength to an explainable four-level priority."""
    if score >= THRESHOLDS["0.5% budget"]:
        return "Critical"
    if score >= THRESHOLDS["1% budget (default)"]:
        return "High"
    if score >= THRESHOLDS["3% budget"]:
        return "Medium"
    return "Low"


def build_explanation(row: pd.Series, budget: str) -> str:
    threshold = THRESHOLDS[budget]
    score = float(row["ocsvm_score"])
    status = str(row["selected_status"])
    severity = str(row["severity"])
    comparison = "equal to or above" if score >= threshold else "below"

    if status == "Anomaly":
        result_text = (
            "The activity is flagged for analyst investigation because its "
            "anomaly score crossed the selected threshold."
        )
    else:
        result_text = (
            "The activity is shown as normal at this operating point because "
            "its anomaly score did not cross the selected threshold."
        )

    return (
        f"The OCSVM anomaly score is {score:.6f}, which is {comparison} the "
        f"{budget} threshold of {threshold:.6f}. Therefore, the selected model "
        f"status is {status} and the dashboard priority is {severity}. "
        f"{result_text} An anomaly is not automatically a confirmed cyberattack."
    )


st.title("🛡️ One-Class SVM Network Anomaly Dashboard")
st.caption(
    "Offline UNSW-NB15 evaluation • Higher OCSVM score means more anomalous"
)

default_csv = find_default_csv()
uploaded_file = None

with st.sidebar:
    st.header("Model settings")
    selected_budget = st.selectbox(
        "False-positive budget",
        list(THRESHOLDS),
        index=1,
        help=(
            "The 1% budget is the notebook's default operating point. "
            "A stricter budget uses a higher anomaly threshold."
        ),
    )
    selected_threshold = THRESHOLDS[selected_budget]
    st.metric("Selected threshold", f"{selected_threshold:.8f}")
    st.info(
        "One-Class SVM was trained on normal traffic only. The notebook reverses "
        "the decision-function sign, so a higher dashboard score means more anomalous."
    )

    if default_csv is None:
        st.subheader("Load results")
        uploaded_file = st.file_uploader(
            "Choose ocsvm_dashboard_results.csv",
            type="csv",
        )

data_source = default_csv if default_csv is not None else uploaded_file

if data_source is None:
    st.warning(
        "Place `ocsvm_dashboard_results.csv` in the `reports`, "
        "`data/model_outputs`, `data`, or project root folder. You can also upload "
        "the CSV from the sidebar."
    )
    st.stop()

try:
    df = load_csv(data_source)
except Exception as exc:
    st.error(f"Could not load the One-Class SVM results: {exc}")
    st.stop()

status_column = STATUS_COLUMNS[selected_budget]
prediction_column = PREDICTION_COLUMNS[selected_budget]
df = df.copy()
df["selected_status"] = df[status_column]
df["selected_prediction"] = df[prediction_column]
df["severity"] = df["ocsvm_score"].apply(assign_severity)

if default_csv is not None:
    st.success(f"Loaded {len(df):,} One-Class SVM records from `{default_csv.name}`.")
else:
    st.success(f"Loaded {len(df):,} One-Class SVM records from the uploaded CSV.")

total_records = len(df)
anomaly_count = int((df["selected_status"] == "Anomaly").sum())
normal_count = int((df["selected_status"] == "Normal").sum())
correct_count = int(
    (df["selected_prediction"].astype(int) == df["actual_label"].astype(int)).sum()
)
accuracy = correct_count / total_records if total_records else 0.0

metric_columns = st.columns(5)
metric_columns[0].metric("Total records", f"{total_records:,}")
metric_columns[1].metric("Anomalies", f"{anomaly_count:,}")
metric_columns[2].metric("Normal", f"{normal_count:,}")
metric_columns[3].metric("Selected threshold", f"{selected_threshold:.6f}")
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
    df["selected_status"].isin(status_options)
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
    "ocsvm_score",
    "selected_status",
    "severity",
    "actual_class",
    "correct_prediction",
]
display_table = filtered[display_columns].rename(
    columns={
        "record_id": "Record ID",
        "ocsvm_score": "OCSVM score",
        "selected_status": "Detection status",
        "severity": "Severity",
        "actual_class": "Actual class",
        "correct_prediction": "Correct at default 1%",
    }
)

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True,
    height=360,
    column_config={
        "OCSVM score": st.column_config.NumberColumn(format="%.6f"),
        "Correct at default 1%": st.column_config.CheckboxColumn(),
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
detail_columns[1].metric("OCSVM score", f"{selected_row['ocsvm_score']:.6f}")
detail_columns[2].metric("Threshold", f"{selected_threshold:.6f}")
detail_columns[3].metric("Status", selected_row["selected_status"])
detail_columns[4].metric("Severity", selected_row["severity"])
detail_columns[5].metric("Actual class", selected_row["actual_class"])

st.markdown("#### Alert explanation")
explanation = build_explanation(selected_row, selected_budget)
if selected_row["selected_status"] == "Anomaly":
    st.warning(explanation)
else:
    st.info(explanation)

with st.expander("Compare all false-positive budgets"):
    comparison = pd.DataFrame(
        {
            "Operating point": ["0.5% budget", "1% budget", "3% budget"],
            "Threshold": [
                THRESHOLDS["0.5% budget"],
                THRESHOLDS["1% budget (default)"],
                THRESHOLDS["3% budget"],
            ],
            "Record status": [
                selected_row["ocsvm_status_0.5pct"],
                selected_row["ocsvm_status_1pct"],
                selected_row["ocsvm_status_3pct"],
            ],
        }
    )
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Threshold": st.column_config.NumberColumn(format="%.8f"),
        },
    )
    st.caption(
        "Severity is an analyst-priority aid based on threshold strength: "
        "Low crosses none, Medium crosses the 3% threshold, High crosses the "
        "1% threshold, and Critical crosses the strict 0.5% threshold."
    )

st.caption(
    "Actual class and correctness are included only for offline evaluation; "
    "they are not used to generate the OCSVM prediction."
)
