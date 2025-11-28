import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# App settings
st.set_page_config(page_title="Airtrol Flow & Error Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("df_clean.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

df = load_data()
st.title("Airtrol Flow & Error Analysis Dashboard")

# Sidebar
st.sidebar.header("Select Time Window")
min_time = df["Timestamp"].min()
max_time = df["Timestamp"].max()

# Date pickers
start_date = st.sidebar.date_input("Start Date", min_time.date(), min_value=min_time.date(), max_value=max_time.date())
start_time = st.sidebar.time_input("Start Time", min_time.time())
end_date = st.sidebar.date_input("End Date", max_time.date(), min_value=min_time.date(), max_value=max_time.date())
end_time = st.sidebar.time_input("End Time", max_time.time())

# Toggle for error percentage line
st.sidebar.header("Display Options")
show_error = st.sidebar.checkbox("Show Error Percentage Line", value=True)

# Combine date & time fields
start_dt = datetime.combine(start_date, start_time)
end_dt = datetime.combine(end_date, end_time)

# Filter dataset
mask = (df["Timestamp"] >= start_dt) & (df["Timestamp"] <= end_dt)
plot_df = df.loc[mask]

if plot_df.empty:
    st.warning("⚠ No data available in the selected time window. Try expanding the range.")
    st.stop()

# Plot
fig = go.Figure()

# Add VFM Flow Rate trace
fig.add_trace(go.Scatter(
    x=plot_df["Timestamp"],
    y=plot_df["VFM Flow Rate (SCFM)"],
    mode="lines",
    name="VFM Flow Rate (SCFM)",
    line=dict(width=2, color="green")
))

# Add Calculated Flow trace
fig.add_trace(go.Scatter(
    x=plot_df["Timestamp"],
    y=plot_df["Flow_Rate_Calculated_SCFM"],
    mode="lines",
    name="Calculated Flow (SCFM)",
    line=dict(width=2, color="orange")
))

# Conditionally add Error Percentage trace
if show_error:
    fig.add_trace(go.Scatter(
        x=plot_df["Timestamp"],
        y=plot_df["Flow_Error_Percentage"],
        mode="lines",
        name="Error Percentage (%)",
        yaxis="y2",
        line=dict(color="red", width=2)
    ))

# Update layout
layout_config = {
    "title": "Flow vs Time with Error Overlay",
    "xaxis": dict(title="Timestamp"),
    "yaxis": dict(
        title="Flow Rate (SCFM)",
        side="left"
    ),
    "hovermode": "x unified",
    "legend": dict(x=0, y=1),
    "height": 600
}

# Add secondary y-axis only if error is shown
if show_error:
    layout_config["yaxis2"] = dict(
        title="Error Percentage (%)",
        overlaying="y",
        side="right",
        color="red",
        range=[-50, 50],
        showgrid=False
    )

fig.update_layout(**layout_config)

st.plotly_chart(fig, use_container_width=True)

# Add info message about clipped errors
max_error = plot_df["Flow_Error_Percentage"].abs().max()
if show_error and max_error > 50:
    st.info(f"ℹ️ Note: Error percentage scale is fixed to ±50% for better visualization. Maximum error in selected window: {max_error:.1f}%")

# Calculate % within spec
abs_err = plot_df["Flow_Error_Percentage"].abs()
accuracy = (abs_err <= 10).mean() * 100

st.subheader("Performance Overview")
col1, col2 = st.columns(2)
col1.metric("% Within ±10% Spec", f"{accuracy:.1f}%")
col2.metric("Max Error %", f"{max_error:.1f}%")
