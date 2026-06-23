"""
Google Drive helper for MI Scouting App.
Uploads photos and videos to a shared Drive folder,
returns viewable/embeddable links.
"""

import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]

# Folder name in Drive where all scout media goes
DRIVE_FOLDER_NAME = "MI_Scout_Media"


@st.cache_resource(ttl=3600)
def get_drive_service():
    """Create an authenticated Google Drive service."""
    if "gcp_service_account" not in st.secrets:
        return None
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


@st.cache_data(ttl=3600)
def get_or_create_folder() -> str:
    """Get or create the MI_Scout_Media folder, return its ID."""
    service = get_drive_service()
    if service is None:
        return ""

    # Search for existing folder
    query = f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        folder_id = files[0]["id"]
    else:
        # Create folder
        metadata = {
            "name": DRIVE_FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = service.files().create(body=metadata, fields="id").execute()
        folder_id = folder["id"]

    # Make folder viewable by anyone with link
    try:
        service.permissions().create(
            fileId=folder_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
    except Exception:
        pass  # Permission might already exist

    return folder_id


def upload_file(file_bytes: bytes, filename: str, mime_type: str, player_name: str = "") -> dict:
    """
    Upload a file to Google Drive.

    Returns dict with:
      - id: Drive file ID
      - viewLink: direct view URL
      - embedLink: embeddable URL (for images)
      - downloadLink: direct download URL
    """
    service = get_drive_service()
    if service is None:
        return {}

    folder_id = get_or_create_folder()
    if not folder_id:
        return {}

    # Prefix filename with player name for organization
    if player_name:
        safe_name = player_name.replace(" ", "_")
        upload_name = f"{safe_name}_{filename}"
    else:
        upload_name = filename

    metadata = {
        "name": upload_name,
        "parents": [folder_id],
    }

    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=mime_type,
        resumable=True,
    )

    uploaded = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, webViewLink, webContentLink",
    ).execute()

    file_id = uploaded["id"]

    # Make file viewable by anyone with link
    try:
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
    except Exception:
        pass

    return {
        "id": file_id,
        "viewLink": f"https://drive.google.com/file/d/{file_id}/view",
        "embedLink": f"https://drive.google.com/thumbnail?id={file_id}&sz=w800",
        "downloadLink": f"https://drive.google.com/uc?export=download&id={file_id}",
    }


def upload_multiple(files: list, player_name: str = "") -> list:
    """
    Upload multiple files. Each item should be a dict with:
      - bytes: file content
      - name: filename
      - type: mime type

    Returns list of upload result dicts.
    """
    results = []
    for f in files:
        result = upload_file(f["bytes"], f["name"], f["type"], player_name)
        if result:
            results.append(result)
    return results


def get_embed_html(file_id: str, mime_type: str = "") -> str:
    """Generate embeddable HTML for a Drive file."""
    if mime_type.startswith("video/"):
        return f'<video controls width="100%" style="border-radius:8px;max-height:400px"><source src="https://drive.google.com/uc?export=download&id={file_id}"><a href="https://drive.google.com/file/d/{file_id}/view">Watch video</a></video>'
    else:
        # Image
        return f'<img src="https://drive.google.com/thumbnail?id={file_id}&sz=w600" style="width:100%;border-radius:8px;max-height:400px;object-fit:contain" />'
