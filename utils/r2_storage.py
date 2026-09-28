"""
Cloudflare R2 storage for MI Scout media uploads.
Uploads files to player-specific folders and returns public URLs.
"""

import streamlit as st
import boto3


def _get_secret(key: str, default: str = "") -> str:
    """Read a secret at call-time (not module load), so secrets are always fresh."""
    try:
        return st.secrets[key]
    except Exception:
        return default


def get_r2_client():
    """Create an S3-compatible client for R2."""
    endpoint = _get_secret("r2_endpoint")
    access_key = _get_secret("r2_access_key")
    secret_key = _get_secret("r2_secret_key")
    if not endpoint or not access_key:
        return None
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def upload_file(file_bytes: bytes, filename: str, mime_type: str, player_name: str = "") -> str:
    """
    Upload a file to R2 in a player-specific folder.
    Returns the public URL of the uploaded file.
    """
    client = get_r2_client()
    if client is None:
        return ""

    bucket = _get_secret("r2_bucket", "miscoutmedia")
    public_url_base = _get_secret("r2_public_url", "")

    # Build the key: PlayerName/filename
    safe_name = player_name.replace(" ", "_").strip() if player_name else "Unknown"
    key = f"{safe_name}/{filename}"

    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType=mime_type,
        )
        public_url = f"{public_url_base}/{key}"
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
