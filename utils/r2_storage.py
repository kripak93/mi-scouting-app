"""
Cloudflare R2 storage for MI Scout media uploads.
Uploads files to player-specific folders and returns public URLs.
"""

import streamlit as st
import boto3

R2_ENDPOINT = st.secrets.get("r2_endpoint", "")
R2_ACCESS_KEY = st.secrets.get("r2_access_key", "")
R2_SECRET_KEY = st.secrets.get("r2_secret_key", "")
R2_BUCKET = st.secrets.get("r2_bucket", "miscoutmedia")
R2_PUBLIC_URL = st.secrets.get("r2_public_url", "")


def get_r2_client():
    """Create an S3-compatible client for R2."""
    if not R2_ENDPOINT or not R2_ACCESS_KEY:
        return None
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
    )


def upload_file(file_bytes: bytes, filename: str, mime_type: str, player_name: str = "") -> str:
    """
    Upload a file to R2 in a player-specific folder.
    Returns the public URL of the uploaded file.
    """
    client = get_r2_client()
    if client is None:
        return ""

    # Build the key: PlayerName/filename
    safe_name = player_name.replace(" ", "_").strip() if player_name else "Unknown"
    key = f"{safe_name}/{filename}"

    try:
        client.put_object(
            Bucket=R2_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=mime_type,
        )
        public_url = f"{R2_PUBLIC_URL}/{key}"
        return public_url
    except Exception as e:
        st.warning(f"Upload failed for {filename}: {str(e)[:80]}")
        return ""


def upload_multiple(files: list, player_name: str = "") -> list:
    """
    Upload multiple files. Returns list of public URLs.
    Each item: {"bytes": bytes, "name": str, "type": str}
    """
    urls = []
    for f in files:
        url = upload_file(f["bytes"], f["name"], f["type"], player_name)
        if url:
            urls.append(url)
    return urls
