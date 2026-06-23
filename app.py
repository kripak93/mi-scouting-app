"""
MI Cricket Intelligence — Scouting App
Home page with navigation to Form and Dashboard.
"""

import streamlit as st

st.set_page_config(
    page_title="MI Cricket Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a3d2b 0%, #2d6a47 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.7); margin-top: 0.5rem; }
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
    }
    .stat-number { font-size: 2rem; font-weight: 700; color: #1a3d2b; }
    .stat-label { font-size: 0.85rem; color: #718096; margin-top: 0.25rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🏏 MI Cricket Intelligence</h1>
    <p>Scout reporting and analytics platform</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 Scouting Form")
    st.write("File a new player scouting report. All the same fields as the mobile form — specialism, batter/bowler assessment, grading, and your gut feel.")
    st.page_link("pages/1_📋_Scouting_Form.py", label="Open Scouting Form →", icon="📋")

with col2:
    st.markdown("### 📊 Dashboard")
    st.write("View all filed reports in real-time. Filter by grade, state, recommendation, urgency. Visualize scouting patterns and hot prospects.")
    st.page_link("pages/2_📊_Dashboard.py", label="Open Dashboard →", icon="📊")

st.markdown("---")
st.caption("MI Cricket Intelligence · Reports sync to Google Sheets in real-time")
