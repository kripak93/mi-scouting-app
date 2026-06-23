"""
MI Cricket Intelligence — Scouting Dashboard
Real-time visualization of all scout reports from Google Sheets.
Password-protected — only ops team can access.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sheets import read_all_reports

st.set_page_config(page_title="Scouting Dashboard", page_icon="📊", layout="wide")

# ── Dashboard Password Protection ──
DASHBOARD_PASSWORD = st.secrets.get("dashboard_password", "MIops2025")

if "dashboard_authenticated" not in st.session_state:
    st.session_state.dashboard_authenticated = False

if not st.session_state.dashboard_authenticated:
    st.markdown("## 🔒 Dashboard Access")
    st.caption("This dashboard is restricted to the MI Cricket Intelligence ops team.")
    pwd = st.text_input("Enter dashboard password", type="password")
    if st.button("Access Dashboard", type="primary"):
        if pwd == DASHBOARD_PASSWORD:
            st.session_state.dashboard_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

st.markdown("## 📊 MI Cricket Intelligence — Scouting Dashboard")

# ── Load data ──
df = read_all_reports()

if df.empty:
    st.info("No reports yet. File your first report from the Scouting Form page.")
    st.stop()

# ── Sidebar Filters ──
st.sidebar.markdown("### 🔍 Filters")

# Grade filter
grades_available = sorted(df["currentGrade"].dropna().unique().tolist()) if "currentGrade" in df.columns else []
grade_filter = st.sidebar.multiselect("Current Grade", grades_available, default=grades_available)

# Recommendation filter
recs_available = sorted(df["recommendation"].dropna().unique().tolist()) if "recommendation" in df.columns else []
rec_filter = st.sidebar.multiselect("Recommendation", recs_available, default=recs_available)

# State filter
states_available = sorted(df["state"].dropna().unique().tolist()) if "state" in df.columns else []
state_filter = st.sidebar.multiselect("State", states_available, default=states_available)

# Specialism filter
specs_available = sorted(df["specialism"].dropna().unique().tolist()) if "specialism" in df.columns else []
spec_filter = st.sidebar.multiselect("Specialism", specs_available, default=specs_available)

# Urgency filter
urgency_available = sorted(df["urgency"].dropna().unique().tolist()) if "urgency" in df.columns else []
urgency_filter = st.sidebar.multiselect("Urgency", urgency_available, default=urgency_available)

# Team filter
teams_available = sorted(df["team"].dropna().unique().tolist()) if "team" in df.columns else []
team_filter = st.sidebar.multiselect("Team", teams_available, default=teams_available)

# Apply filters
filtered = df.copy()
if "currentGrade" in filtered.columns:
    filtered = filtered[filtered["currentGrade"].isin(grade_filter)]
if "recommendation" in filtered.columns:
    filtered = filtered[filtered["recommendation"].isin(rec_filter)]
if "state" in filtered.columns:
    filtered = filtered[filtered["state"].isin(state_filter)]
if "specialism" in filtered.columns:
    filtered = filtered[filtered["specialism"].isin(spec_filter)]
if "urgency" in filtered.columns:
    filtered = filtered[filtered["urgency"].isin(urgency_filter)]
if "team" in filtered.columns:
    filtered = filtered[filtered["team"].isin(team_filter)]

st.caption(f"Showing {len(filtered)} of {len(df)} reports")

# ══════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Reports", len(filtered))
with col2:
    hot = len(filtered[filtered.get("urgency", pd.Series()) == "Hot Prospect"]) if "urgency" in filtered.columns else 0
    st.metric("🔥 Hot Prospects", hot)
with col3:
    sign_now = len(filtered[filtered.get("recommendation", pd.Series()) == "Sign Now"]) if "recommendation" in filtered.columns else 0
    st.metric("Sign Now", sign_now)
with col4:
    scouts = filtered["scoutName"].nunique() if "scoutName" in filtered.columns else 0
    st.metric("Active Scouts", scouts)
with col5:
    states_count = filtered["state"].nunique() if "state" in filtered.columns else 0
    st.metric("States Covered", states_count)

# ══════════════════════════════════════
# CHARTS
# ══════════════════════════════════════
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Player Table", "📊 Grade Distribution", "🗺️ By State", "📈 Timeline"])

with tab1:
    # Player table with key columns
    display_cols = ["firstName", "lastName", "state", "specialism", "currentGrade",
                    "recommendation", "urgency", "dateWatched", "scoutName", "comparedTo"]
    available_cols = [c for c in display_cols if c in filtered.columns]

    if available_cols:
        table_df = filtered[available_cols].copy()
        # Highlight hot prospects
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "firstName": "First Name",
                "lastName": "Last Name",
                "state": "State",
                "specialism": "Specialism",
                "currentGrade": "Grade",
                "recommendation": "Rec",
                "urgency": "Urgency",
                "dateWatched": "Date Watched",
                "scoutName": "Scout",
                "comparedTo": "Compared To",
            },
        )
    else:
        st.write("No data columns available to display.")

with tab2:
    if "currentGrade" in filtered.columns and len(filtered) > 0:
        grade_order = ["A+", "A", "B+", "B", "C"]
        grade_counts = filtered["currentGrade"].value_counts().reindex(grade_order).dropna()
        fig = px.bar(
            x=grade_counts.index,
            y=grade_counts.values,
            labels={"x": "Grade", "y": "Count"},
            title="Current Grade Distribution",
            color=grade_counts.index,
            color_discrete_map={"A+": "#1a3d2b", "A": "#2d6a47", "B+": "#e8a020", "B": "#718096", "C": "#c53030"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Recommendation breakdown
        if "recommendation" in filtered.columns:
            rec_counts = filtered["recommendation"].value_counts()
            fig2 = px.pie(
                values=rec_counts.values,
                names=rec_counts.index,
                title="Recommendation Breakdown",
                color_discrete_sequence=["#1a3d2b", "#2d6a47", "#e8a020", "#718096"],
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No grade data to visualize.")

with tab3:
    if "state" in filtered.columns and len(filtered) > 0:
        state_counts = filtered["state"].value_counts().head(15)
        fig = px.bar(
            x=state_counts.values,
            y=state_counts.index,
            orientation="h",
            labels={"x": "Reports", "y": "State"},
            title="Reports by State (Top 15)",
            color=state_counts.values,
            color_continuous_scale=["#e8f5ee", "#1a3d2b"],
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        # Specialism by state heatmap
        if "specialism" in filtered.columns:
            cross = pd.crosstab(filtered["state"], filtered["specialism"])
            if len(cross) > 0:
                fig2 = px.imshow(
                    cross,
                    title="Specialism × State Heatmap",
                    color_continuous_scale=["#fff", "#1a3d2b"],
                    aspect="auto",
                )
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No state data to visualize.")

with tab4:
    if "dateWatched" in filtered.columns and len(filtered) > 0:
        timeline = filtered.copy()
        timeline["dateWatched"] = pd.to_datetime(timeline["dateWatched"], errors="coerce")
        timeline = timeline.dropna(subset=["dateWatched"])
        if len(timeline) > 0:
            daily = timeline.groupby(timeline["dateWatched"].dt.date).size().reset_index(name="count")
            daily.columns = ["date", "count"]
            fig = px.line(
                daily,
                x="date",
                y="count",
                title="Reports Filed Over Time",
                markers=True,
            )
            fig.update_traces(line_color="#1a3d2b")
            st.plotly_chart(fig, use_container_width=True)

            # Cumulative
            daily["cumulative"] = daily["count"].cumsum()
            fig2 = px.area(
                daily,
                x="date",
                y="cumulative",
                title="Cumulative Reports",
            )
            fig2.update_traces(line_color="#e8a020", fillcolor="rgba(232,160,32,0.2)")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No valid dates to chart.")
    else:
        st.info("No date data available.")

# ══════════════════════════════════════
# DETAILED PLAYER VIEW
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 🔎 Player Detail View")

if len(filtered) > 0 and "firstName" in filtered.columns and "lastName" in filtered.columns:
    player_names = (filtered["firstName"].fillna("") + " " + filtered["lastName"].fillna("")).tolist()
    selected = st.selectbox("Select a player to view full report", [""] + player_names)

    if selected:
        idx = player_names.index(selected)
        player = filtered.iloc[idx]

        col1, col2 = st.columns([1, 2])
        with col1:
            grade = player.get("currentGrade", "—")
            grade_color = "#1a3d2b" if grade == "A+" else "#2d6a47" if grade == "A" else "#e8a020" if grade == "B+" else "#718096"
            st.markdown(f"""
            <div style="background:{grade_color};color:white;padding:2rem;border-radius:12px;text-align:center">
                <div style="font-size:2.5rem;font-weight:700">{grade}</div>
                <div style="font-size:0.85rem;opacity:0.8">Current Grade</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Ceiling:** {player.get('ceilingGrade', '—')}")
            st.markdown(f"**Recommendation:** {player.get('recommendation', '—')}")
            st.markdown(f"**Urgency:** {player.get('urgency', '—')}")

        with col2:
            st.markdown(f"**{selected}** · {player.get('specialism', '')} · {player.get('state', '')}")
            st.markdown(f"**Age:** {player.get('age', '—')} | **Hand:** {player.get('handedness', '—')} | **Height:** {player.get('height', '—')}")
            st.markdown(f"**Watched:** {player.get('dateWatched', '—')} · {player.get('context', '')} · {player.get('competition', '')}")
            if player.get("comparedTo"):
                st.info(f"🔄 **Compared to:** {player['comparedTo']}")
            if player.get("finalWord"):
                st.markdown(f"> ✍️ *\"{player['finalWord']}\"*")
            if player.get("scoutName"):
                st.caption(f"Filed by {player['scoutName']} · {player.get('submittedAt', '')}")

        # ── Media Gallery ──
        media_ids = player.get("mediaFileIds", "")
        if media_ids and str(media_ids).strip():
            st.markdown("#### 📸 Photos & Videos")
            file_ids = [fid.strip() for fid in str(media_ids).split(",") if fid.strip()]
            cols = st.columns(min(len(file_ids), 3))
            for i, fid in enumerate(file_ids):
                with cols[i % 3]:
                    # Try to display as image first (Drive thumbnail)
                    img_url = f"https://drive.google.com/thumbnail?id={fid}&sz=w400"
                    view_url = f"https://drive.google.com/file/d/{fid}/view"
                    st.markdown(
                        f'<a href="{view_url}" target="_blank">'
                        f'<img src="{img_url}" style="width:100%;border-radius:8px;margin-bottom:8px;cursor:pointer" />'
                        f'</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"[Open full size ↗]({view_url})")

        # External video links
        video_links = player.get("videos", "")
        if video_links and str(video_links).strip():
            st.markdown("#### 🎥 Video Links")
            for link in str(video_links).strip().split("\n"):
                link = link.strip()
                if not link:
                    continue
                if "youtube.com" in link or "youtu.be" in link:
                    st.video(link)
                elif "instagram.com" in link:
                    st.markdown(f"📺 [Instagram clip]({link})")
                else:
                    st.markdown(f"🔗 [{link}]({link})")
else:
    st.info("No players to display.")

# ── Refresh button ──
st.markdown("---")
if st.button("🔄 Refresh data"):
    read_all_reports.clear()
    st.rerun()
