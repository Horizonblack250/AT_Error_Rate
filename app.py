import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Airtrol Error Analysis Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("df_clean.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

df = load_data()

st.title("Airtrol Flow & Error Analysis Dashboard")

# Sidebar selection
st.sidebar.header("Time Range Filter")

min_time = df["Timestamp"].min()
max_time = df["Timestamp"].max()

start_time = st.sidebar.slider("Select start time",
                               min_value=min_time,
                               max_value=max_time,
                               value=min_time,
                               format="YYYY-MM-DD HH:mm:ss")

end_time = st.sidebar.slider("Select end time",
                             min_value=min_time,
                             max_value=max_time,
                             value=max_time,
                             format="YYYY-MM-DD HH:mm:ss")

# Filter data by time
mask = (df["Timestamp"] >= start_time) & (df["Timestamp"] <= end_time)
plot_df = df.loc[mask].copy()

if plot_df.empty:
    st.warning("No data found in selected range.")
    st.stop()

# Plotting
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=plot_df["Timestamp"],
    y=plot_df["VFM Flow Rate (SCFM)"],
    mode="lines",
    name="VFM Flow Rate (SCFM)",
    line=dict(width=2)
))

fig.add_trace(go.Scatter(
    x=plot_df["Timestamp"],
    y=plot_df["Flow_Rate_Calculated_SCFM"],
    mode="lines",
    name="Calculated Flow (SCFM)",
    line=dict(dash="dash", width=2)
))

fig.add_trace(go.Scatter(
    x=plot_df["Timestamp"],
    y=plot_df["Flow_Error_Percentage"],
    mode="lines",
    name="Error Percentage (%)",
    yaxis="y2",
    line=dict(color="red", width=2)
))

fig.update_layout(
    title="Flow Comparison & Error %",
    xaxis=dict(title="Timestamp"),
    yaxis=dict(title="Flow (SCFM)"),
    yaxis2=dict(
        title="Error Percentage (%)",
        overlaying="y",
        side="right",
        color="red"
    ),
    hovermode="x unified",
    legend=dict(x=0, y=1)
)

st.plotly_chart(fig, use_container_width=True)
