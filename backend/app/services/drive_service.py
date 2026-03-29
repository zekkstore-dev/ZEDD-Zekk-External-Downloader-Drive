import os
from pathlib import Path
from ..core.config import LOCAL_MODE, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES
from .downloader import guess_mime

# #bahasa indonesia: Memuat pustaka Google OAuth hanya jika diperlukan (menghemat memori)
if not LOCAL_MODE:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import google.auth.transport.requests

def create_flow():
    """Membuat objek flow untuk proses OAuth Google™."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Google Client ID/Secret belum diatur di .env!")
        
    return Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

def get_credentials(session: dict):
    """Mendapatkan objek credentials dari data sesi."""
    creds = Credentials(
        token=session["access_token"],
        refresh_token=session.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )

    # #bahasa indonesia: Refresh token otomatis jika sudah lama/kedaluwarsa
    if creds.expired and creds.refresh_token:
        creds.refresh(google.auth.transport.requests.Request())
        session["access_token"] = creds.token

    return creds

def upload_to_drive(creds, file_path: str, folder_id: str = "", jobs: dict = {}, job_id: str = "") -> dict:
    """Mengunggah file ke Google Drive."""
    service = build("drive", "v3", credentials=creds)
    file_name = Path(file_path).name
    mime_type = guess_mime(file_path)
    file_metadata = {"name": file_name}

    if folder_id:
        file_metadata["parents"] = [folder_id]
    else:
        # #bahasa indonesia: Cari folder default 'ZEDD_DOWNLOADS' di Drive, buat jika tidak ada
        query = "name='ZEDD_DOWNLOADS' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id)").execute()
        folders = results.get("files", [])
        if folders:
            file_metadata["parents"] = [folders[0]["id"]]
        else:
            folder_meta = {"name": "ZEDD_DOWNLOADS", "mimeType": "application/vnd.google-apps.folder"}
            folder = service.files().create(body=folder_meta, fields="id").execute()
            file_metadata["parents"] = [folder["id"]]

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True, chunksize=5 * 1024 * 1024)
    request = service.files().create(body=file_metadata, media_body=media, fields="id, name, webViewLink")

    # #bahasa indonesia: Proses unggah dilakukan dalam potongan (chunks) agar progress real-time bisa dikirim ke User
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status and job_id in jobs:
            upload_pct = int(status.progress() * 100)
            # Progress bar frontend (60% - 95% dialokasikan untuk fase upload)
            jobs[job_id]["progress"] = 60 + int(upload_pct * 0.35)
            jobs[job_id]["status_text"] = f"Mengunggah ke Drive... ({upload_pct}%)"

    return response
