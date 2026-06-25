"""
MI Cricket Intelligence — Scouting Form
Scouts land directly on the form. No sidebar, no dashboard.
Uses radio buttons (not dropdowns) and dynamic conditional sections.
"""

import streamlit as st
from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.sheets import append_report
from utils.drive import upload_multiple

st.set_page_config(page_title="MI Scout Report", page_icon="🏏", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    header [data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

if "scout_logged_in" not in st.session_state:
    st.session_state.scout_logged_in = False
if "players_filed" not in st.session_state:
    st.session_state.players_filed = 0

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh",
    "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Hyderabad", "Jammu & Kashmir", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Mumbai", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Saurashtra",
    "Services", "Sikkim", "Tamil Nadu", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "Vidarbha", "West Bengal",
]

# ══════════════════════════════════════
# SCOUT LOGIN
# ══════════════════════════════════════
if not st.session_state.scout_logged_in:
    st.markdown("## 🏏 MI Cricket Intelligence — Scout Report")
    st.caption("Log in once, then file as many reports as you like.")
    col1, col2 = st.columns(2)
    with col1:
        scout_first = st.text_input("First name *", placeholder="Ravi")
    with col2:
        scout_last = st.text_input("Last name *", placeholder="Kumar")
    scout_team = st.radio("Scouting for *", ["MI Men", "MI Women"], horizontal=True)
    if st.button("Start filing reports →", type="primary"):
        if not scout_first or not scout_last:
            st.error("Please enter your first and last name.")
        else:
            st.session_state.scout_logged_in = True
            st.session_state.scout_name = f"{scout_first} {scout_last}"
            st.session_state.scout_team = scout_team
            st.rerun()
    st.stop()

# ══════════════════════════════════════
# LOGGED IN — DYNAMIC FORM (no st.form, so conditionals work)
# ══════════════════════════════════════
col_info, col_logout = st.columns([4, 1])
with col_info:
    st.markdown(f"**Scout:** {st.session_state.scout_name} · {st.session_state.scout_team} · Reports filed: {st.session_state.players_filed}")
with col_logout:
    if st.button("🚪 Log out"):
        st.session_state.scout_logged_in = False
        st.session_state.players_filed = 0
        st.rerun()
st.markdown("---")

# ── Player Identity ──
st.markdown("### 🏏 Player Identity")
col1, col2 = st.columns(2)
with col1:
    p_first = st.text_input("First name *", placeholder="Arjun")
with col2:
    p_last = st.text_input("Last name *", placeholder="Sharma")
col1, col2 = st.columns(2)
with col1:
    p_age = st.number_input("Age", min_value=13, max_value=45, value=None)
with col2:
    p_height = st.radio("Height", ["Short (<5'7\")", "Medium (5'7\"–5'11\")", "Tall (6'0\"–6'3\")", "Very tall (6'4\"+)"], index=None, horizontal=True)
p_state = st.selectbox("State Association *", [""] + STATES)

# ── Sighting Context ──
st.markdown("### 📍 Sighting Context")
col1, col2 = st.columns(2)
with col1:
    p_date = st.date_input("Date watched *", value=date.today())
with col2:
    p_how = st.multiselect("Watched how", ["Live at ground", "TV / Video"], default=[])
p_context = st.radio("Match context *", ["State League", "BCCI Domestic", "Centre of Excellence", "Local League", "Hinterland Spotting"], index=None, horizontal=True)

# Dynamic tournament list based on context + team
STATE_LEAGUES_MEN = [
    "T20 Mumbai", "TNPL", "Maharaja T20", "Delhi PL", "UPT20",
    "Vidarbha PL", "Baroda PL", "MP League", "Bengal T20",
    "Saurashtra PL", "Chhattisgarh PL", "Chandigarh PL",
    "Andhra PL", "Jharkhand T20", "Telangana T20 (TG20)",
    "Pondicherry PL", "Assam PL", "Other State League",
]
STATE_LEAGUES_WOMEN = [
    "T20 Mumbai (W)", "TNPL (W)", "Delhi PL (W)", "UPT20 (W)",
    "Vidarbha PL (W)", "Baroda PL (W)", "MP League (W)", "Bengal T20 (W)",
    "Andhra PL (W)", "Jharkhand T20 (W)", "Telangana T20 (W)",
    "Pondicherry PL (W)", "Assam T20 (W)", "Other State League (W)",
]
BCCI_DOMESTIC_MEN = [
    "Ranji Trophy", "Vijay Hazare Trophy", "Syed Mushtaq Ali Trophy",
    "Duleep Trophy", "Deodhar Trophy", "CK Nayudu Trophy",
    "Cooch Behar Trophy", "Other BCCI Domestic",
]
BCCI_DOMESTIC_WOMEN = [
    "Senior Women's T20", "Women's Senior One Day",
    "Senior Women's Challenger", "Women's U19 T20",
    "Other BCCI Domestic (W)",
]

p_comp = ""
if p_context == "State League":
    leagues = STATE_LEAGUES_WOMEN if st.session_state.scout_team == "MI Women" else STATE_LEAGUES_MEN
    p_comp = st.selectbox("Tournament name", [""] + leagues)
elif p_context == "BCCI Domestic":
    domestic = BCCI_DOMESTIC_WOMEN if st.session_state.scout_team == "MI Women" else BCCI_DOMESTIC_MEN
    p_comp = st.selectbox("Tournament name", [""] + domestic)
elif p_context:
    p_comp = st.text_input("Tournament / league name", placeholder="e.g. name of the event...")

# ── Specialism (this drives conditional sections) ──
st.markdown("### ⚡ Player Specialism")
p_spec = st.radio("Specialism *", ["Pure Batter", "Pure Bowler", "Bat/WK", "Bat AR Seam", "Bat AR Spin", "Bowl AR Seam", "Bowl AR Spin"], index=None, horizontal=True)
p_hand = st.radio("Batting hand", ["RHB", "LHB"], index=None, horizontal=True)

is_bat = p_spec in ["Pure Batter", "Bat/WK", "Bat AR Seam", "Bat AR Spin"]
is_bowl = p_spec in ["Pure Bowler", "Bowl AR Seam", "Bowl AR Spin", "Bat AR Seam", "Bat AR Spin"]
is_wk = p_spec == "Bat/WK"

p_btype = ""
if is_bowl:
    p_btype = st.radio("Bowling type", ["RAF", "RFM", "RMP", "LAF", "LFM", "LMP", "LAO", "LAUO", "RALS", "Mystery"], index=None, horizontal=True)

# ── Batter Assessment (only shows when specialism is batting) ──
bat_pos = bat_hspd = bat_swing = bat_power = ""
bat_power_narr = bat_gaps = bat_field = bat_readvar = bat_readvar_narr = ""
bat_smarts = []
if is_bat:
    st.markdown("### 🏏 Batter Assessment")
    bat_pos = st.radio("Position", ["Opener", "No. 3", "Middle Order"], index=None, horizontal=True)
    bat_hspd = st.radio("Hand speed", ["Exceptional", "Fast", "Moderate"], index=None, horizontal=True)
    bat_swing = st.radio("Bat swing", ["Exceptional", "Very Good", "Good"], index=None, horizontal=True)
    bat_power = st.radio("Power hitting", ["Exceptional", "Very Good", "Good", "Developing"], index=None, horizontal=True)
    bat_power_narr = st.text_area("Power hitting moment", placeholder="A shot or moment that showed their power level...")
    bat_gaps = st.text_area("Gaps ability", placeholder="How they found gaps and manipulated the field...")
    bat_field = st.text_area("Does the batter play the field?", placeholder="Reading placements, hitting into gaps...")
    bat_readvar = st.radio("Reading variations under pressure", ["Exceptional", "Good", "Struggled", "Too early to tell"], index=None, horizontal=True)
    bat_readvar_narr = st.text_area("Variations moment", placeholder="A delivery that showed how they read the ball...")
    bat_smarts = st.multiselect("Game smarts — batting intelligence", ["Reads the game well", "Rotates strike smartly", "Adapts to situation", "Good under pressure", "Picks gaps instinctively", "Controls tempo", "Reads bowler's plans", "Strong decision-making"])

# ── Bowler Assessment (only shows when specialism is bowling) ──
bowl_pace = bowl_speed = bowl_fieldsetting = ""
bowl_fs_narr = bowl_varpressure = ""
bowl_skills = []
bowl_phases = []
bowl_smarts = []
if is_bowl:
    st.markdown("### 🎯 Bowler Assessment")
    bowl_pace = st.radio("Pace category", ["Express", "Fast", "Fast-Medium", "Medium"], index=None, horizontal=True)
    bowl_speed = st.text_input("Speed on the gun (kph)", placeholder="e.g. 138-142")
    bowl_skills = st.multiselect("Skills identified", ["Swing", "Seam", "Sharp bouncer", "Deceptive slower", "Slow bouncer", "Heel + wide yorker", "Heel only", "Wide only"])
    bowl_fieldsetting = st.radio("Field setting & ball choice", ["Exceptional", "Very Good", "Good", "Can Improve"], index=None, horizontal=True)
    bowl_fs_narr = st.text_area("Tactical moment", placeholder="A specific over that showed their tactical thinking...")
    bowl_varpressure = st.radio("Under pressure", ["Executed well", "Inconsistent", "Too early to tell"], index=None, horizontal=True)
    bowl_phases = st.multiselect("Phases assessed", ["Powerplay (1–6)", "Middle (7–15)", "Death (16–20)"])
    bowl_smarts = st.multiselect("Game smarts — bowling intelligence", ["Reads batters well", "Adapts plans mid-over", "Sets up dismissals", "Good under pressure", "Controls pace changes", "Smart field placement", "Responds well to boundaries", "Thinks ahead of the batter"])

# ── Wicketkeeper (only shows for Bat/WK) ──
wk_gloves = wk_notes = ""
if is_wk:
    st.markdown("### 🧤 Wicketkeeper")
    wk_gloves = st.radio("Glove work", ["Exceptional", "Very Good", "Good"], index=None, horizontal=True)
    wk_notes = st.text_area("WK notes", placeholder="Angles, footwork, stumpings...")

# ── Fielding ──
st.markdown("### 🤸 Fielding and Athleticism")
f_athletic = st.radio("Athletic base", ["Good fielder + runner", "Good fielder", "Good runner", "Needs development"], index=None, horizontal=True)
col1, col2 = st.columns(2)
with col1:
    f_catching = st.radio("Catching", ["Exceptional", "Good", "Unreliable"], index=None)
with col2:
    f_arm = st.radio("Throwing arm", ["Strong", "Average", "Weak"], index=None)
f_pos = st.text_input("Best position in the field", placeholder="e.g. Cover point, Fine leg...")

# ── Player Comparison ──
st.markdown("### 🔄 Player Comparison")
p_compared = st.text_area("Who does this player remind you of?", placeholder="e.g. Plays like Samson but with better temperament...")

# ── Background ──
st.markdown("### 📖 Background and Journey")
p_background = st.text_area("Background", placeholder="Where are they from? How did they get into cricket?...")

# ── Media ──
st.markdown("### 🎥 Photos, Videos & Profiles")
uploaded_files = st.file_uploader(
    "Upload photos or videos (scorecards, action shots, clips)",
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi", "webm"],
)
p_videos = st.text_area("Video links", placeholder="YouTube, Instagram URLs — one per line")
col1, col2 = st.columns(2)
with col1:
    p_cricinfo = st.text_input("ESPNcricinfo profile")
with col2:
    p_cricheros = st.text_input("Cricheros profile")

# ── Grading (simplified) ──
st.markdown("### ⭐ Grading")
cgrade = st.radio("Current ability grade *", ["A+", "A", "B+", "B", "C"], index=None, horizontal=True)
ceil_grade = st.radio("Ceiling grade (2–3 years)", ["A+", "A", "B+", "B", "C"], index=None, horizontal=True)
rec = st.radio("Recommendation *", ["Invite to Trial", "Monitor", "Pass"], index=None, horizontal=True)
urgency = st.radio("Urgency", ["Hot Prospect", "Normal", "Low Priority"], index=None, horizontal=True)

# ── Final Word (the most important part) ──
st.markdown("### ✍️ The Scout's Final Word")
st.caption("In your own words — what did you *feel* about this player? Your gut. First thoughts.")
final_word = st.text_area("Your final word", placeholder="This is your space. Tell us what you really think...", height=150)

# ── Submit ──
st.markdown("---")
if st.button("Save player report ✓", type="primary", use_container_width=True):
    errors = []
    if not p_first:
        errors.append("Player first name")
    if not p_last:
        errors.append("Player last name")
    if not p_state:
        errors.append("State association")
    if not p_context:
        errors.append("Match context")
    if not p_spec:
        errors.append("Specialism")
    if not cgrade:
        errors.append("Current grade")
    if not rec:
        errors.append("Recommendation")

    if errors:
        st.error(f"Missing required fields: {', '.join(errors)}")
    else:
        report = {
            "submittedAt": datetime.now().isoformat(),
            "scoutName": st.session_state.scout_name,
            "team": st.session_state.scout_team,
            "firstName": p_first,
            "lastName": p_last,
            "age": p_age or "",
            "height": p_height or "",
            "state": p_state,
            "dateWatched": str(p_date),
            "context": p_context or "",
            "competition": p_comp,
            "watchedHow": p_how,
            "specialism": p_spec or "",
            "handedness": p_hand or "",
            "bowlerType": p_btype or "",
            "battingPosition": bat_pos or "",
            "handSpeed": bat_hspd or "",
            "batSwing": bat_swing or "",
            "powerHitting": bat_power or "",
            "powerNarrative": bat_power_narr,
            "gapsAbility": bat_gaps,
            "playsField": bat_field,
            "readVariations": bat_readvar or "",
            "readVarNarrative": bat_readvar_narr,
            "batterSmarts": bat_smarts,
            "pace": bowl_pace or "",
            "bowlingSpeed": bowl_speed,
            "skills": bowl_skills,
            "variations": "",
            "fieldSetting": bowl_fieldsetting or "",
            "fieldSettingNarrative": bowl_fs_narr,
            "varPressure": bowl_varpressure or "",
            "pressureNarrative": "",
            "difficultOvers": "",
            "phases": bowl_phases,
            "bowlerSmarts": bowl_smarts,
            "gloves": wk_gloves or "",
            "wkNotes": wk_notes,
            "athletic": f_athletic or "",
            "catching": f_catching or "",
            "arm": f_arm or "",
            "fieldPos": f_pos,
            "comparedTo": p_compared,
            "background": p_background,
            "videos": p_videos,
            "cricinfo": p_cricinfo,
            "cricheros": p_cricheros,
            "currentGrade": cgrade or "",
            "ceilingGrade": ceil_grade or "",
            "recommendation": rec or "",
            "urgency": urgency or "",
            "finalWord": final_word,
        }

        with st.spinner("Saving to MI Cricket Intelligence..."):
            media_links = []
            if uploaded_files:
                files_to_upload = [{"bytes": uf.getvalue(), "name": uf.name, "type": uf.type} for uf in uploaded_files]
                media_links = upload_multiple(files_to_upload, player_name=f"{p_first} {p_last}")
                report["mediaFileIds"] = ", ".join(m["id"] for m in media_links)
                if media_links and "folderLink" in media_links[0]:
                    report["playerMediaFolder"] = media_links[0]["folderLink"]

            success = append_report(report)

        if success:
            st.session_state.players_filed += 1
            st.success(f"✅ {p_first} {p_last} saved! ({st.session_state.players_filed} players filed)")
            st.balloons()
        else:
            st.error("Failed to save. Check connection.")
