from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

def upload_to_drive(file_path: str, filename: str, creds_dict: dict):
    """
    Mengunggah file ke Google Drive.
    """
    # Bahasa Indonesia: Inisialisasi API Google Drive dengan token user
    creds = Credentials.from_authorized_user_info(creds_dict)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': filename}
    media = MediaFileUpload(file_path, resumable=True)
    
    # Proses upload ke folder root atau folder tertentu
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Komentar: Service ini fokus pada komunikasi dengan Google Cloud API.
