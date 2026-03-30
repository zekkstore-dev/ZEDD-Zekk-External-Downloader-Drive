import subprocess
import os
from pathlib import Path
import yt_dlp
from ..core.config import DOWNLOAD_TEMP_DIR

def get_video_info(url: str):
    """
    Mengambil informasi video tanpa mendownload.
    """
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def run_download(url: str, output_path: str, progress_callback=None):
    """
    Logika utama pengunduhan menggunakan yt-dlp.
    """
    # Bahasa Indonesia: Mengatur opsi download agar efisien
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_callback] if progress_callback else [],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error download: {e}")
        return False

# Komentar: Logika ini menangani interaksi langsung dengan library yt-dlp.
