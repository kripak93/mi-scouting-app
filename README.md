# MI Cricket Intelligence — Scouting App

Streamlit multi-page app for MI cricket scouting operations.

## Structure

```
MI_Scouting_App/
├── app.py                      # Home page
├── pages/
│   ├── 1_📋_Scouting_Form.py  # Full scouting form
│   └── 2_📊_Dashboard.py      # Real-time analytics dashboard
├── utils/
│   └── sheets.py              # Google Sheets read/write helper
├── .streamlit/
│   ├── config.toml            # Theme and server config
│   └── secrets.toml.template  # Secrets template (copy to secrets.toml)
├── requirements.txt
└── README.md
```

## Setup

### 1. Install dependencies

```bash
cd MI_Scouting_App
pip install -r requirements.txt
```

### 2. Google Sheets API setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the **Google Sheets API** and **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **Service Account**
5. Download the JSON key file
6. Open your Google Sheet and click **Share**
7. Share with the service account email (e.g. `my-scout@project.iam.gserviceaccount.com`)
   - Give it **Editor** access

### 3. Configure secrets

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `secrets.toml`:
- Set `spreadsheet_id` to your Sheet ID (from the URL)
- Paste the service account JSON key contents under `[gcp_service_account]`

### 4. Run locally

```bash
streamlit run app.py
```

Opens at http://localhost:8501

## Features

### Scouting Form (Page 1)
- Scout login with identity persistence
- Full player assessment matching the mobile HTML form
- Batter/bowler/WK conditional sections
- Player comparison field ("who do they remind you of?")
- Bowling speed (kph) field
- Writes directly to Google Sheets

### Dashboard (Page 2)
- Real-time data from the same Google Sheet
- Filters: grade, recommendation, state, specialism, urgency, team
- KPI cards: total reports, hot prospects, sign now, active scouts
- Charts: grade distribution, reports by state, heatmap, timeline
- Detailed player view with full report expand

## Deployment (Streamlit Cloud)

1. Push to GitHub (ensure `.gitignore` excludes secrets)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file to `app.py`
4. In **Secrets** settings, paste your `secrets.toml` contents
5. Deploy

## Connecting to the HTML Form

Both this Streamlit app and the `mi_scout_report.html` mobile form write to
the same Google Sheet. The HTML form uses a Google Apps Script web app as a
POST endpoint. The Streamlit app uses the Sheets API directly via a service
account.

The Dashboard page reads from the Sheet regardless of how the data was
written — so reports from mobile scouts using the HTML form appear in the
dashboard automatically.
