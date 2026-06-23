"""
MI Cricket Intelligence — Scouting Form
Full scouting form matching the mobile HTML version.
"""

import streamlit as st
from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sheets import append_report
from utils.drive import upload_multiple

st.set_page_config(page_title="Scout Report", page_icon="📋", layout="centered")

# ── Session state for scout identity ──
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

REGIONS = [
    "Andhra Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Hyderabad",
    "Jammu & Kashmir", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mumbai", "Nagaland", "Odisha",
    "Punjab", "Rajasthan", "Saurashtra", "Tamil Nadu", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "Vidarbha", "West Bengal", "Multiple states",
]


# ══════════════════════════════════════
# SCOUT LOGIN
# ══════════════════════════════════════
if not st.session_state.scout_logged_in:
    st.markdown("## 🧑 Scout Login")
    st.caption("Your name stays on every report you file today")

    col1, col2 = st.columns(2)
    with col1:
        scout_first = st.text_input("First name *", placeholder="Ravi")
    with col2:
        scout_last = st.text_input("Last name *", placeholder="Kumar")

    scout_phone = st.text_input("Mobile number", placeholder="+91 98765 43210")
    scout_region = st.selectbox("Your scouting region", [""] + REGIONS)
    scout_team = st.radio("Scouting for *", ["MI Men", "MI Women"], horizontal=True)

    if st.button("Start filing reports →", type="primary"):
        if not scout_first or not scout_last:
            st.error("Please enter your first and last name.")
        else:
            st.session_state.scout_logged_in = True
            st.session_state.scout_name = f"{scout_first} {scout_last}"
            st.session_state.scout_phone = scout_phone
            st.session_state.scout_region = scout_region
            st.session_state.scout_team = scout_team
            st.rerun()
    st.stop()

# ══════════════════════════════════════
# LOGGED IN — SHOW FORM
# ══════════════════════════════════════
st.markdown(f"**Scout:** {st.session_state.scout_name} · {st.session_state.scout_team} · Reports filed: {st.session_state.players_filed}")
st.markdown("---")

with st.form("player_report", clear_on_submit=True):
    # ── Player Identity ──
    st.markdown("### 🏏 Player Identity")
    col1, col2 = st.columns(2)
    with col1:
        p_first = st.text_input("First name *", placeholder="Arjun", key="pf")
    with col2:
        p_last = st.text_input("Last name *", placeholder="Sharma", key="pl")

    col1, col2 = st.columns(2)
    with col1:
        p_age = st.number_input("Age", min_value=13, max_value=45, value=None, key="pa")
    with col2:
        p_height = st.selectbox("Height", ["", "Short (under 5'7\")", "Medium (5'7\"–5'11\")", "Tall (6'0\"–6'3\")", "Very tall (6'4\"+)"])

    p_state = st.selectbox("State Association *", [""] + STATES)

    # ── Sighting Context ──
    st.markdown("### 📍 Sighting Context")
    col1, col2 = st.columns(2)
    with col1:
        p_date = st.date_input("Date watched *", value=date.today())
    with col2:
        p_how = st.radio("Watched", ["Live at ground", "TV / Video"], horizontal=True)

    p_context = st.selectbox("Match context *", ["", "State League", "BCCI Domestic", "Centre of Excellence", "Local League", "Hinterland Spotting"])
    p_comp = st.text_input("Tournament / league name", placeholder="e.g. Vijay Hazare, DY Patil T20...")

    # ── Specialism ──
    st.markdown("### ⚡ Player Specialism")
    p_spec = st.selectbox("Specialism *", ["", "Pure Batter", "Pure Bowler", "Bat/WK", "Bat AR Seam", "Bat AR Spin", "Bowl AR Seam", "Bowl AR Spin"])
    p_hand = st.radio("Batting hand", ["RHB", "LHB"], horizontal=True)

    is_bat = p_spec in ["Pure Batter", "Bat/WK", "Bat AR Seam", "Bat AR Spin"]
    is_bowl = p_spec in ["Pure Bowler", "Bowl AR Seam", "Bowl AR Spin", "Bat AR Seam", "Bat AR Spin"]
    is_wk = p_spec == "Bat/WK"

    p_btype = ""
    if is_bowl:
        p_btype = st.selectbox("Bowling type", ["", "RAF", "LAF", "LAO", "LAUO", "RALS", "Mystery"])

    # ── Batter Assessment ──
    bat_pos = bat_hspd = bat_swing = bat_power = ""
    bat_power_narr = bat_gaps = bat_field = bat_readvar = bat_readvar_narr = bat_smarts = ""
    if is_bat:
        st.markdown("### 🏏 Batter Assessment")
        bat_pos = st.selectbox("Position", ["", "Opener", "No. 3", "Middle Order"])
        bat_hspd = st.selectbox("Hand speed", ["", "Exceptional", "Fast", "Moderate"])
        bat_swing = st.selectbox("Bat swing", ["", "Exceptional", "Very Good", "Good"])
        bat_power = st.selectbox("Power hitting ability", ["", "Exceptional", "Very Good", "Good", "Developing"])
        bat_power_narr = st.text_area("Power hitting moment", placeholder="A shot or moment that showed their power level...")
        bat_gaps = st.text_area("Gaps ability and creative mindset", placeholder="How they found gaps...")
        bat_field = st.text_area("Does the batter play the field?", placeholder="Reading placements...")
        bat_readvar = st.selectbox("Reading variations under pressure", ["", "Exceptional", "Good", "Struggled", "Too early to tell"])
        bat_readvar_narr = st.text_area("Variations moment", placeholder="A delivery that showed how they read the ball...")
        bat_smarts = st.text_area("Game smarts — batting intelligence", placeholder="Walk me through what you saw...")

    # ── Bowler Assessment ──
    bowl_pace = bowl_speed = bowl_variations = bowl_fieldsetting = ""
    bowl_fs_narr = bowl_varpressure = bowl_pressure_narr = bowl_diff = bowl_smarts = ""
    bowl_skills = []
    bowl_phases = []
    if is_bowl:
        st.markdown("### 🎯 Bowler Assessment")
        bowl_pace = st.selectbox("Pace category", ["", "Express", "Fast", "Fast-Medium", "Medium"])
        bowl_speed = st.text_input("Speed on the gun (kph)", placeholder="e.g. 138-142")
        bowl_skills = st.multiselect("Skills identified", ["Swing", "Seam", "Sharp bouncer", "Deceptive slower (dipping)", "Deceptive slow bouncer", "Heel + wide yorker", "Heel only", "Wide only"])
        bowl_variations = st.text_area("Variations picked up", placeholder="Both the ones that worked and under pressure...")
        bowl_fieldsetting = st.selectbox("Field setting and ball choice", ["", "Exceptional", "Very Good", "Good", "Can Improve"])
        bowl_fs_narr = st.text_area("Tactical moment", placeholder="A specific over that showed their tactical thinking...")
        bowl_varpressure = st.selectbox("Speed and length under pressure", ["", "Executed under pressure", "Inconsistent under pressure", "Too early to tell"])
        bowl_pressure_narr = st.text_area("Pressure moment", placeholder="When the game was tight...")
        st.markdown("**⚡ The difficult overs**")
        st.caption("Did you see them bowl powerplay, overs 16–18, or the final over with the game on the line?")
        bowl_diff = st.text_area("Difficult overs", placeholder="Which overs? What happened?...", key="diff")
        bowl_phases = st.multiselect("Phases assessed", ["Powerplay (1–6)", "Middle (7–15)", "Death (16–20)"])
        bowl_smarts = st.text_area("Game smarts — bowling intelligence", placeholder="How did they think through their spell?...")

    # ── Wicketkeeper ──
    wk_gloves = wk_notes = ""
    if is_wk:
        st.markdown("### 🧤 Wicketkeeper")
        wk_gloves = st.selectbox("Glove work", ["", "Exceptional", "Very Good", "Good"])
        wk_notes = st.text_area("WK notes", placeholder="Angles, footwork, stumpings...")

    # ── Fielding ──
    st.markdown("### 🤸 Fielding and Athleticism")
    f_athletic = st.selectbox("Athletic base", ["", "Good fielder + runner", "Good fielder", "Good runner", "Needs development"])
    col1, col2 = st.columns(2)
    with col1:
        f_catching = st.selectbox("Catching", ["", "Exceptional", "Good", "Unreliable"])
    with col2:
        f_arm = st.selectbox("Throwing arm", ["", "Strong", "Average", "Weak"])
    f_pos = st.text_input("Best position in the field", placeholder="e.g. Cover point, Fine leg...")

    # ── Player Comparison (NEW) ──
    st.markdown("### 🔄 Player Comparison")
    st.caption("Think about style, temperament, shot selection — not stats.")
    p_compared = st.text_area("Who does this player remind you of?", placeholder="e.g. Plays like Samson but with better temperament...")

    # ── Background ──
    st.markdown("### 📖 Background and Journey")
    p_background = st.text_area("Background", placeholder="Where are they from? How did they get into cricket?...")

    # ── Media ──
    st.markdown("### 🎥 Video and Profiles")
    st.markdown("#### 📸 Upload Photos & Videos")
    st.caption("Scorecards, action shots, batting grip, short clips. Max 10 files, 50MB each.")
    uploaded_files = st.file_uploader(
        "Choose photos or videos",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi", "webm"],
        key="media_upload",
    )
    st.markdown("#### 🔗 External Links")
    p_videos = st.text_area("Video links", placeholder="YouTube, Instagram URLs — one per line")
    p_cricinfo = st.text_input("ESPNcricinfo profile", placeholder="https://espncricinfo.com/player/...")
    p_cricheros = st.text_input("Cricheros profile", placeholder="https://cricheros.com/...")

    # ── Grading ──
    st.markdown("### ⭐ Your Grading")
    cgrade = st.selectbox("Current ability grade *", ["", "A+", "A", "B+", "B", "C"])
    cgrade_reason = st.text_area("What makes you give this grade?", key="cgr")
    ceil_grade = st.selectbox("Ceiling grade (2–3 years)", ["", "A+", "A", "B+", "B", "C"])
    ceil_reason = st.text_area("What would need to happen for them to reach that ceiling?", key="clr")

    role_fit = st.multiselect("T20 role fit", ["Powerplay batter", "Anchor batter", "Finisher", "Powerplay bowler", "Middle overs specialist", "Death bowler", "WK batter"])

    rec = st.selectbox("Recommendation *", ["", "Sign Now", "Invite to Trial", "Monitor", "Pass"])
    urgency = st.selectbox("Urgency", ["", "Hot Prospect", "Normal", "Low Priority"])
    trial = st.text_area("Trial recommendation", placeholder="Would you call them to our performance centre — and why?")

    # ── Final Word ──
    st.markdown("### ✍️ The Scout's Final Word")
    st.caption("In your own words — what did you *feel* about this player? Your gut.")
    final_word = st.text_area("Your final word", placeholder="This is your space. Tell us what you really think...", key="fw")
    anything_else = st.text_area("Anything else?", placeholder="Anything that didn't fit above...")

    # ── Submit ──
    submitted = st.form_submit_button("Save player report ✓", type="primary")

    if submitted:
        # Validation
        errors = []
        if not p_first:
            errors.append("Player first name is required")
        if not p_last:
            errors.append("Player last name is required")
        if not p_state:
            errors.append("State association is required")
        if not p_context:
            errors.append("Match context is required")
        if not p_spec:
            errors.append("Specialism is required")
        if not cgrade:
            errors.append("Current ability grade is required")
        if not rec:
            errors.append("Recommendation is required")

        if errors:
            for e in errors:
                st.error(e)
        else:
            report = {
                "submittedAt": datetime.now().isoformat(),
                "scoutName": st.session_state.scout_name,
                "scoutPhone": st.session_state.scout_phone,
                "scoutRegion": st.session_state.scout_region,
                "team": st.session_state.scout_team,
                "firstName": p_first,
                "lastName": p_last,
                "age": p_age or "",
                "height": p_height,
                "state": p_state,
                "dateWatched": str(p_date),
                "context": p_context,
                "competition": p_comp,
                "watchedHow": p_how,
                "specialism": p_spec,
                "handedness": p_hand,
                "bowlerType": p_btype,
                "battingPosition": bat_pos,
                "handSpeed": bat_hspd,
                "batSwing": bat_swing,
                "powerHitting": bat_power,
                "powerNarrative": bat_power_narr,
                "gapsAbility": bat_gaps,
                "playsField": bat_field,
                "readVariations": bat_readvar,
                "readVarNarrative": bat_readvar_narr,
                "batterSmarts": bat_smarts,
                "pace": bowl_pace,
                "bowlingSpeed": bowl_speed,
                "skills": bowl_skills,
                "variations": bowl_variations,
                "fieldSetting": bowl_fieldsetting,
                "fieldSettingNarrative": bowl_fs_narr,
                "varPressure": bowl_varpressure,
                "pressureNarrative": bowl_pressure_narr,
                "difficultOvers": bowl_diff,
                "phases": bowl_phases,
                "bowlerSmarts": bowl_smarts,
                "gloves": wk_gloves,
                "wkNotes": wk_notes,
                "athletic": f_athletic,
                "catching": f_catching,
                "arm": f_arm,
                "fieldPos": f_pos,
                "comparedTo": p_compared,
                "background": p_background,
                "videos": p_videos,
                "cricinfo": p_cricinfo,
                "cricheros": p_cricheros,
                "currentGrade": cgrade,
                "currentGradeReason": cgrade_reason,
                "ceilingGrade": ceil_grade,
                "ceilingReason": ceil_reason,
                "roleFit": role_fit,
                "recommendation": rec,
                "urgency": urgency,
                "trial": trial,
                "finalWord": final_word,
                "anythingElse": anything_else,
            }

            with st.spinner("Saving to MI Cricket Intelligence..."):
                # Upload media files to Drive
                media_links = []
                if uploaded_files:
                    files_to_upload = []
                    for uf in uploaded_files:
                        files_to_upload.append({
                            "bytes": uf.getvalue(),
                            "name": uf.name,
                            "type": uf.type,
                        })
                    media_links = upload_multiple(files_to_upload, player_name=f"{p_first} {p_last}")
                    # Add Drive links to report
                    photo_links = [m["viewLink"] for m in media_links if not m.get("type", "").startswith("video/")]
                    report["photoLinks"] = ", ".join(photo_links) if photo_links else ""
                    report["mediaFileIds"] = ", ".join(m["id"] for m in media_links)
                    # Show upload count
                    st.info(f"📤 Uploaded {len(media_links)} file(s) to Google Drive")

                success = append_report(report)

            if success:
                st.session_state.players_filed += 1
                st.success(f"✅ {p_first} {p_last} saved! ({st.session_state.players_filed} players filed this session)")
                st.balloons()
            else:
                st.error("Failed to save. Check your Google Sheets connection.")
