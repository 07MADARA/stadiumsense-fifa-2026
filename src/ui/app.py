import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Page Configuration
st.set_page_config(
    page_title="StadiumSense AI | FIFA 2026",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high contrast and modern aesthetics
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2e7d32;
    }
    .stMetric[data-testid="stMetricValue"] {
        color: #e0e0e0;
    }
    .critical {
        border-left: 5px solid #d32f2f !important;
    }
    .warning {
        border-left: 5px solid #f57c00 !important;
    }
    .header-style {
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    .ai-insight-box {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)


def fetch_telemetry():
    """Fetches real-time simulated telemetry from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/telemetry")
        if response.status_code == 200:
            return response.json()
        st.error(f"Failed to fetch data: {response.status_code}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to backend API. Please ensure the FastAPI server is running.")
        return None

def fetch_insights(telemetry_data):
    """Fetches AI insights from the backend based on telemetry data."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/insights", json={"telemetry": telemetry_data})
        if response.status_code == 200:
            return response.json().get("insights", "No insights returned.")
        return f"Error: Backend returned {response.status_code}"
    except Exception as e:
        return f"Error connecting to AI service: {e}"

# Dashboard Header
st.markdown("<h1 class='header-style'>🏟️ StadiumSense AI Command Center</h1>", unsafe_allow_html=True)
st.markdown("Real-time Operational Intelligence for **FIFA World Cup 2026**")
st.divider()


col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Live Sensor Telemetry (Zone Congestion)")
    
    # Auto-refresh button (mock for simulation)
    if st.button("🔄 Refresh Telemetry"):
        pass # Streamlit reruns on button click automatically

    with st.spinner("Fetching live IoT data..."):
        telemetry = fetch_telemetry()
        
    if telemetry:
        zones = telemetry.get("stadium_zones", [])
        
        # Display summary metrics
        total_occupancy = sum(z["current_occupancy"] for z in zones)
        total_capacity = sum(z["max_capacity"] for z in zones)
        overall_density = round((total_occupancy / total_capacity) * 100, 1)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Overall Stadium Density", f"{overall_density}%")
        m2.metric("Total Occupants (Sample)", f"{total_occupancy}")
        critical_zones = sum(1 for z in zones if z["status"] == "Critical Bottleneck")
        m3.metric("Critical Zones", f"{critical_zones}")

        # Display Data Table
        df = pd.DataFrame(zones)
        # Reorder and rename columns for display
        display_df = df[['zone_name', 'zone_type', 'density_percentage', 'status']]
        display_df.columns = ['Zone', 'Type', 'Density (%)', 'Status']
        
        # Apply conditional formatting
        def color_status(val):
            if val == 'Critical Bottleneck':
                return 'color: #ff4b4b; font-weight: bold'
            elif val == 'Warning - High Density':
                return 'color: #ffa500; font-weight: bold'
            return 'color: #00fa9a'
            
        st.dataframe(
            display_df.style.map(color_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )

with col_right:
    st.subheader("🧠 GenAI Operational Insights")
    
    if telemetry:
        with st.spinner("Analyzing telemetry with Gemini 1.5 Flash..."):
            insights = fetch_insights(telemetry)
            
        st.markdown(f"""
        <div class="ai-insight-box">
            <h4>⚡ Immediate Action Plan</h4>
            <div>{insights}</div>
        </div>
        """, unsafe_allow_html=True)
        
st.sidebar.markdown("### System Status")
st.sidebar.success("🟢 API Connected")
if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_api_key_here":
    st.sidebar.success("🟢 Gemini API Ready")
else:
    st.sidebar.warning("🟡 Gemini API Key missing (.env)")
    
st.sidebar.info("Data updates every few seconds in a real production environment. Click 'Refresh Telemetry' to simulate the next tick.")
