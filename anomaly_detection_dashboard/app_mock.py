from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Network Anomaly Dashboard",
    layout="wide",
)

st.title("Network Anomaly Dashboard")

st.info(
    "Synthetic mock data for dashboard development only. "
    "These records are not real model outputs."
)

data_file = Path(__file__).with_name("mock_alerts.csv")
alerts = pd.read_csv(data_file)

st.subheader("Mock Alert Dataset")
st.dataframe(alerts, use_container_width=True, hide_index=True)

st.subheader("Alert Details")

selected_alert = st.selectbox(
    "Select an alert",
    range(len(alerts)),
    format_func=lambda row: (
        f"{alerts.loc[row, 'source_ip']} to "
        f"{alerts.loc[row, 'destination_ip']}"
    ),
)

alert = alerts.iloc[selected_alert]

column1, column2, column3 = st.columns(3)

column1.metric("Source IP", alert["source_ip"])
column2.metric("Destination IP", alert["destination_ip"])
column3.metric("Anomaly Score", f"{alert['anomaly_score']:.2f}")

st.write(f"**Severity:** {alert['severity']}")
st.write(f"**Explanation:** {alert['explanation']}")