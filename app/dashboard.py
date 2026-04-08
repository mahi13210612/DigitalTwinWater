import sys
import os
# Add project root to path so 'src' module is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import time
from sklearn.linear_model import LinearRegression

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("💧 Digital Twin - Smart Water Monitoring System")

# =========================
# SESSION STATE INIT
# =========================
if "live_data" not in st.session_state:
    st.session_state.live_data = []

# =========================
# READ REAL SENSOR VALUE
# No random fallback — only real hardware data
# =========================
def get_sensor_value_safe():
    """
    Read from Arduino serial (COM3).
    Returns (int, status) or (None, status) if sensor unavailable.
    """
    try:
        from src.serial_read import get_sensor_value
        value = get_sensor_value()
        if value is not None:
            return value, "🟢 sensor"
        return None, "🟡 no data"
    except Exception as e:
        print(f"[Dashboard] Serial error: {e}")
        return None, "🔴 error"

# =========================
# FIREBASE UPLOAD — only real values
# =========================
def try_firebase_upload(value):
    """Upload only if value is real (not None)."""
    if value is None:
        return "⏭ skipped"
    try:
        from src.firebase_upload import upload_sensor_value
        success = upload_sensor_value(value)
        return "✅ saved" if success else "❌ failed"
    except Exception as e:
        print(f"[Firebase] {e}")
        return "❌ error"

# =========================
# GET SENSOR + UPLOAD
# =========================
sensor_value, sensor_source = get_sensor_value_safe()
if sensor_value is None:
    sensor_value = 0
firebase_status = try_firebase_upload(sensor_value)

# Only append REAL values to live data
if sensor_value is not None:
    st.session_state.live_data.append(sensor_value)
    st.session_state.live_data = st.session_state.live_data[-100:]

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🔧 Control Panel")
refresh_rate = st.sidebar.slider("Auto Refresh (seconds)", 1, 30, 1)
threshold = st.sidebar.slider("Anomaly Threshold", 5, 300, 50)

st.sidebar.markdown("### 📌 Project Info")
st.sidebar.info("""
Digital Twin System for Smart Water Monitoring
- Machine Learning Prediction
- Anomaly Detection
- Real-time Monitoring
""")

st.sidebar.markdown("### 👩‍💻 Developer")
st.sidebar.write("Mahitha M.P")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔥 Firebase Status")
st.sidebar.write(f"Last upload: {firebase_status}")

st.sidebar.markdown("### 📡 Sensor Status")
st.sidebar.write(f"Source: {sensor_source}")
st.sidebar.write(f"Value: {sensor_value if sensor_value is not None else 'waiting...'}")

# =========================
# LOAD HISTORICAL DATA
# =========================
try:
    hist_df = pd.read_csv("data/water_data.csv")
    if "Water_Usage" not in hist_df.columns:
        hist_df.rename(columns={hist_df.columns[0]: "Water_Usage"}, inplace=True)
except Exception as e:
    st.warning(f"CSV load failed: {e}")
    hist_df = pd.DataFrame({"Water_Usage": [10] * 10})

hist_df = hist_df[["Water_Usage"]].copy()
hist_df["Time"] = range(len(hist_df))

# =========================
# LIVE DATAFRAME
# =========================
live_df = pd.DataFrame({
    "Water_Usage": st.session_state.live_data,
    "Time": range(len(st.session_state.live_data))
})

# =========================
# ML — HISTORICAL
# =========================
if len(hist_df) > 1:
    m1 = LinearRegression().fit(hist_df[["Time"]], hist_df["Water_Usage"])
    hist_df["Predicted"] = m1.predict(hist_df[["Time"]])
else:
    hist_df["Predicted"] = hist_df["Water_Usage"]

# =========================
# ML — LIVE
# =========================
if len(live_df) > 1:
    m2 = LinearRegression().fit(live_df[["Time"]], live_df["Water_Usage"])
    live_df["Predicted"] = m2.predict(live_df[["Time"]])
else:
    live_df["Predicted"] = live_df["Water_Usage"]

# =========================
# ANOMALY DETECTION
# =========================
combined = pd.concat(
    [hist_df[["Water_Usage", "Predicted"]], live_df[["Water_Usage", "Predicted"]]],
    ignore_index=True
)
combined["Status"] = combined.apply(
    lambda row: "Abnormal" if abs(row["Water_Usage"] - row["Predicted"]) > threshold else "Normal",
    axis=1
)
abnormal_count = int((combined["Status"] == "Abnormal").sum())

# =========================
# LAYOUT
# =========================
col_main, col_side = st.columns([3, 1])

with col_main:

    # METRICS
    st.subheader("� System Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Data", len(combined))
    c2.metric("Live Value", sensor_value if sensor_value is not None else "—")
    c3.metric("Abnormal Events", abnormal_count)
    c4.metric("Live Points", len(st.session_state.live_data))

    if abnormal_count > 10:
        st.error("⚠️ High anomalies detected!")
    else:
        st.success("✅ System Normal")

    # GRAPH 1 — HISTORICAL
    st.subheader("📈 Graph 1: Historical Data")
    st.line_chart(hist_df.set_index("Time")[["Water_Usage", "Predicted"]])

    # GRAPH 2 — LIVE
    st.subheader("� Graph 2: Live Sensor Data (Last 50 Points)")
    if len(live_df) >= 2:
        live_display = live_df.tail(50)
        st.line_chart(live_display.set_index("Time")[["Water_Usage", "Predicted"]])
    elif len(live_df) == 1:
        st.line_chart(live_df.set_index("Time")[["Water_Usage"]])
    else:
        st.info("⏳ Waiting for sensor data... Make sure Arduino is connected on COM3.")

    # DATA SOURCE DISTRIBUTION
    st.subheader("� Data Source Distribution")
    st.bar_chart(pd.Series({"Historical": len(hist_df), "Live": len(live_df)}))

    # ABNORMAL EVENTS
    st.subheader("🚨 Abnormal Events")
    abnormal_data = combined[combined["Status"] == "Abnormal"]
    if len(abnormal_data) > 0:
        st.dataframe(abnormal_data.tail(20))
    else:
        st.write("No abnormal events detected.")

    if st.checkbox("Show Full Dataset"):
        st.dataframe(combined)

with col_side:

    st.subheader("� Insights")
    if len(combined) > 0:
        st.metric("Max Usage", round(combined["Water_Usage"].max(), 2))
        st.metric("Min Usage", round(combined["Water_Usage"].min(), 2))

    st.markdown("---")
    st.subheader("� Alerts")
    if abnormal_count > 10:
        st.warning("Too many anomalies!")
    else:
        st.success("System Stable")

    st.markdown("---")
    st.subheader("📊 Quick Stats")
    if len(combined) > 0:
        st.write("Std Dev:", round(combined["Water_Usage"].std(), 2))
        st.write("Median:", round(combined["Water_Usage"].median(), 2))

    st.markdown("---")
    st.subheader("💧 Tank Level")
    tank_val = sensor_value if sensor_value is not None else 0
    tank_percent = min(max(tank_val, 0), 100)
    st.progress(tank_percent)
    st.write(f"{tank_percent}% Full")

# =========================
# AUTO REFRESH — safe pattern
# time.sleep + st.rerun() at end of script
# session_state persists across reruns so live_data keeps growing
# =========================
st.markdown("---")
st.caption(f"🔄 Refreshing every {refresh_rate}s · {sensor_source} · Firebase: {firebase_status}")

time.sleep(refresh_rate)
st.rerun()
