"""
Google Sheets helper for MI Scouting App.

Supports two modes:
1. SERVICE ACCOUNT mode (full read/write via Sheets API)
   - Requires gcp_service_account in secrets.toml
2. APPS SCRIPT mode (fallback — reads via published Sheet CSV, writes via Apps Script POST)
   - Only requires apps_script_url and published_csv_url in secrets.toml
   - Simpler setup, no service account needed
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Determine which mode we're in
HAS_SERVICE_ACCOUNT = "gcp_service_account" in st.secrets
APPS_SCRIPT_URL = st.secrets.get("apps_script_url", "https://script.google.com/macros/s/AKfycbwo4Tgx858H727F-4XrzNKzafxVCYStwu3d85P7Z1bwzCJHzS8TNbSOFdS3zYJk_sIH/exec")
PUBLISHED_CSV_URL = st.secrets.get("published_csv_url", "")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Sheet config
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "")
SHEET_NAME = st.secrets.get("sheet_name", "Sheet1")


@st.cache_resource(ttl=300)
def get_gspread_client():
    """Create an authenticated gspread client from Streamlit secrets."""
    if not HAS_SERVICE_ACCOUNT:
        return None
    import gspread
    from google.oauth2.service_account import Credentials
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet():
    """Get the target worksheet."""
    import gspread
    client = get_gspread_client()
    if client is None:
        return None
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet.worksheet(SHEET_NAME)


@st.cache_data(ttl=60)
def read_all_reports() -> pd.DataFrame:
    """Read all scout reports from the sheet into a DataFrame."""
    # Mode 1: Service Account (full API access)
    if HAS_SERVICE_ACCOUNT and SPREADSHEET_ID:
        try:
            ws = get_worksheet()
            if ws is None:
                return pd.DataFrame()
            data = ws.get_all_records()
            if not data:
                return pd.DataFrame()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error reading sheet via API: {e}")
            return pd.DataFrame()

    # Mode 2: Published CSV URL (no service account needed)
    if PUBLISHED_CSV_URL:
        try:
            df = pd.read_csv(PUBLISHED_CSV_URL)
            return df
        except Exception as e:
            st.error(f"Error reading published CSV: {e}")
            return pd.DataFrame()

    st.warning("No data source configured. Add either `gcp_service_account` or `published_csv_url` to secrets.toml")
    return pd.DataFrame()


def append_report(report: dict) -> bool:
    """Append a single player report."""
    # Mode 1: Service Account
    if HAS_SERVICE_ACCOUNT and SPREADSHEET_ID:
        try:
            ws = get_worksheet()
            if ws is None:
                return _append_via_apps_script(report)

            headers = ws.row_values(1)
            if not headers:
                headers = list(report.keys())
                ws.append_row(headers)

            row = []
            for h in headers:
                val = report.get(h, "")
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                row.append(str(val) if val is not None else "")

            new_cols = [k for k in report.keys() if k not in headers]
            if new_cols:
                for col in new_cols:
                    headers.append(col)
                    val = report.get(col, "")
                    if isinstance(val, list):
                        val = ", ".join(str(v) for v in val)
                    row.append(str(val) if val is not None else "")
                ws.update("A1", [headers])

            ws.append_row(row, value_input_option="USER_ENTERED")
            read_all_reports.clear()
            return True
        except Exception as e:
            st.error(f"Error writing via API: {e}")
            return _append_via_apps_script(report)

    # Mode 2: Apps Script POST
    return _append_via_apps_script(report)


def _append_via_apps_script(report: dict) -> bool:
    """Fallback: POST to Apps Script endpoint (same as HTML form uses)."""
    try:
        # Format lists as strings
        clean_report = {}
        for k, v in report.items():
            if isinstance(v, list):
                clean_report[k] = ", ".join(str(x) for x in v)
            else:
                clean_report[k] = v

        payload = {
            "submittedAt": report.get("submittedAt", datetime.now().isoformat()),
            "scoutName": report.get("scoutName", ""),
            "scoutPhone": report.get("scoutPhone", ""),
            "scoutRegion": report.get("scoutRegion", ""),
            "team": report.get("team", ""),
            "players": [clean_report],
        }

        resp = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        # Apps Script redirects on success (302/303) or returns 200
        read_all_reports.clear()
        return True
    except Exception as e:
        st.error(f"Error posting to Apps Script: {e}")
        return False
