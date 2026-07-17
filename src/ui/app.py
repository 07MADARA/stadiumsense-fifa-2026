"""
Streamlit dashboard for StadiumSense AI.
Provides real-time visualization of stadium telemetry and AI insights.
"""

import sys
import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import time
from typing import Dict, Any, Optional

# Add the root project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.simulator import generate_telemetry_data
from src.api.agent import get_actionable_insights

load_dotenv()


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


def fetch_telemetry() -> Optional[Dict[str, Any]]:
    """
    Simulates real-time telemetry data directly.
    
    Returns:
        Optional[Dict[str, Any]]: The telemetry data, or None if an error occurs.
    """
    try:
        return generate_telemetry_data()
    except Exception as e:
        st.error(f"Failed to generate telemetry data: {e}")
        return None

@st.cache_data(ttl=30, show_spinner=False)
def fetch_insights(telemetry_data: Dict[str, Any]) -> str:
    """
    Fetches AI insights directly using the Gemini API.
    
    Args:
        telemetry_data (Dict[str, Any]): The telemetry data to analyze.
        
    Returns:
        str: The AI-generated actionable insights.
    """
    try:
        return get_actionable_insights(telemetry_data)
    except Exception as e:
        return f"Error generating insights: {e}"


# Dashboard Header using semantic standard Streamlit components
st.title("🏟️ StadiumSense AI Command Center")
st.markdown("Real-time Operational Intelligence for **FIFA World Cup 2026**")
st.divider()


col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Live Sensor Telemetry (Zone Congestion)")
    
    # Auto-refresh button (mock for simulation)
    if st.button("🔄 Refresh Telemetry", help="Fetch the latest IoT sensor readings"):
        pass # Streamlit reruns on button click automatically

    with st.spinner("Fetching live IoT data..."):
        telemetry = fetch_telemetry()
        
    if telemetry:
        zones = telemetry.get("stadium_zones", [])
        
        # Display summary metrics
        total_occupancy = sum(z["current_occupancy"] for z in zones)
        total_capacity = sum(z["max_capacity"] for z in zones)
        overall_density = round((total_occupancy / total_capacity) * 100, 1) if total_capacity else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Overall Stadium Density", f"{overall_density}%", help="Total occupancy vs total capacity")
        m2.metric("Total Occupants (Sample)", f"{total_occupancy}", help="Current estimated people count")
        critical_zones = sum(1 for z in zones if z["status"] == "Critical Bottleneck")
        m3.metric("Critical Zones", f"{critical_zones}", help="Zones exceeding 90% capacity")

        # Display Data Table
        df = pd.DataFrame(zones)
        
        # Enhance accessibility by adding icons to the status column
        def append_status_icon(row: pd.Series) -> str:
            if row['status'] == 'Critical Bottleneck':
                return '🔴 Critical Bottleneck'
            elif row['status'] == 'Warning - High Density':
                return '🟠 Warning - High Density'
            return '🟢 Normal'
            
        df['status_display'] = df.apply(append_status_icon, axis=1)

        # Reorder and rename columns for display
        display_df = df[['zone_name', 'zone_type', 'sensor_type', 'density_percentage', 'trend', 'status_display']]
        display_df.columns = ['Zone', 'Type', 'Sensor', 'Density (%)', 'Trend', 'Status']
        
        # Apply conditional formatting
        def color_status(val: str) -> str:
            if 'Critical' in val:
                return 'color: #ff4b4b; font-weight: bold'
            elif 'Warning' in val:
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
        with st.spinner("Analyzing telemetry with Gemini 2.5 Flash..."):
            insights = fetch_insights(telemetry)
            
        st.markdown(f"""
        <div class="ai-insight-box" aria-label="AI Generated Insights">
            <h4>⚡ Immediate Action Plan</h4>
            <div>{insights}</div>
        </div>
        """, unsafe_allow_html=True)
        
st.sidebar.markdown("### System Status")
st.sidebar.success("🟢 StadiumSense Core: Active")

# Check API key from env or st.secrets
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except FileNotFoundError:
        pass
    except Exception:
        pass

if api_key and api_key != "your_api_key_here":
    st.sidebar.success("🟢 Gemini API Ready")
else:
    st.sidebar.warning("🟡 Gemini API Key missing (Settings -> Secrets)")
    
st.sidebar.info("Data updates every few seconds in a real production environment. Click 'Refresh Telemetry' to simulate the next tick.")
