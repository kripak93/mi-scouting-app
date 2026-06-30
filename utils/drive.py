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
    "https://www.googleapis.com/auth/drive",
]

# Folder ID — this is a folder in your personal Drive shared with the service account
DRIVE_FOLDER_ID = "1OLVXTd9ZkuDluGooDlKEr0gfDeopqppH"


@st.cache_resource(ttl=3600)
def get_drive_service():
    """Create an authenticated Google Drive service."""
    if "gcp_service_account" not in st.secrets:
        return None
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def get_or_create_folder() -> str:
    """Return the hardcoded folder ID (owned by your personal account)."""
    return DRIVE_FOLDER_ID


def upload_file(file_bytes: bytes, filename: str, mime_type: str, player_name: str = "") -> dict:
    """
    Upload a file to Google Drive inside a player-specific subfolder.

    Returns dict with:
      - id: Drive file ID
      - viewLink: direct view URL
      - embedLink: embeddable URL (for images)
      - downloadLink: direct download URL
      - folderLink: link to the player's folder
    """
    service = get_drive_service()
    if service is None:
        return {}

    folder_id = get_or_create_folder()
    if not folder_id:
        return {}

    # Create a player-specific subfolder
    player_folder_id = folder_id
    if player_name:
        safe_name = player_name.strip().replace(" ", "_")
        player_folder_id = _get_or_create_subfolder(service, folder_id, safe_name)

    # Prefix filename with player name for extra clarity
    if player_name:
        safe_name = player_name.replace(" ", "_")
        upload_name = f"{safe_name}_{filename}"
    else:
        upload_name = filename

    metadata = {
        "name": upload_name,
        "parents": [player_folder_id],
    }

    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=mime_type,
        resumable=len(file_bytes) > 5 * 1024 * 1024,  # Only resumable for files > 5MB
    )

    try:
        uploaded = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink, webContentLink",
        ).execute()
    except Exception as e:
        st.warning(f"Upload failed for {filename}: {str(e)[:100]}")
        return {}

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
        "folderLink": f"https://drive.google.com/drive/folders/{player_folder_id}",
    }


def _get_or_create_subfolder(service, parent_id: str, folder_name: str) -> str:
    """Get or create a subfolder inside the parent folder."""
    query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    files = results.get("files", [])

    if files:
        return files[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    subfolder_id = folder["id"]

    # Make subfolder viewable
    try:
        service.permissions().create(
            fileId=subfolder_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
    except Exception:
        pass

    return subfolder_id


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
