import streamlit as st
import pandas as pd
from datetime import date

# Set Streamlit page config
st.set_page_config(layout="wide")

# Load today’s merged data
today_str = date.today().strftime("%Y-%m-%d")
file_path = f"data/dashboard_merged_{today_str}.csv"

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"🚫 File not found: {file_path}")
    st.stop()

# Convert edges to numeric and scale to percent
df["edge_over"] = pd.to_numeric(df["edge_over"], errors="coerce") * 100
df["edge_under"] = pd.to_numeric(df["edge_under"], errors="coerce") * 100

# Round values for display
df["line"] = df["line"].round(1)
df["expected_innings"] = df["expected_innings"].round(2)
df["projected_ks"] = df["projected_ks"].round(2)
df["edge_over"] = df["edge_over"].round(2)
df["edge_under"] = df["edge_under"].round(2)

# Sort by highest edge (either over or under)
df["max_edge"] = df[["edge_over", "edge_under"]].max(axis=1)
df = df.sort_values(by="max_edge", ascending=False).drop(columns=["max_edge"])

# Filter rows
positive_mask = (df["edge_over"] > 0) | (df["edge_under"] > 0)
df_positive = df[positive_mask].copy()
df_negative = df[~positive_mask].copy()

# Format percent columns with color
def highlight_edges(val):
    try:
        val = float(val)
        color = "green" if val > 0 else "red"
        return f"color: {color}"
    except:
        return ""

# Display
st.title(f"🎯 Pitcher K Edge Dashboard — {today_str}")

st.subheader("✅ Today's Plays (Positive Edges)")
if df_positive.empty:
    st.write("No positive edges today.")
else:
    st.dataframe(
        df_positive[
            [
                "Date",
                "bookmaker",
                "pitcher_name",
                "line",
                "over_odds",
                "under_odds",
                "expected_innings",
                "projected_ks",
                "edge_over",
                "edge_under",
            ]
        ].style.applymap(highlight_edges, subset=["edge_over", "edge_under"])
        .format({
            "edge_over": "{:.2f}%",
            "edge_under": "{:.2f}%",
            "expected_innings": "{:.2f}",
            "projected_ks": "{:.2f}",
            "line": "{:.1f}"
        })
    )

st.subheader("⚠️ Leans Against (Negative or Neutral Edges)")
if df_negative.empty:
    st.write("No neutral/negative edges today.")
else:
    st.dataframe(
        df_negative[
            [
                "Date",
                "bookmaker",
                "pitcher_name",
                "line",
                "over_odds",
                "under_odds",
                "expected_innings",
                "projected_ks",
                "edge_over",
                "edge_under",
            ]
        ].style.applymap(highlight_edges, subset=["edge_over", "edge_under"])
        .format({
            "edge_over": "{:.2f}%",
            "edge_under": "{:.2f}%",
            "expected_innings": "{:.2f}",
            "projected_ks": "{:.2f}",
            "line": "{:.1f}"
        })
    )
