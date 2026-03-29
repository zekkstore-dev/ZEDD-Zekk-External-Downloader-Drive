import os
import asyncio
import subprocess
import shutil
import tempfile
from pathlib import Path
from ..core.config import get_local_dl_dir

# #bahasa indonesia: Fungsi pembantu untuk mengunduh secara langsung menggunakan urllib (fallback)
# Jika yt-dlp gagal, kita pakai ini sebagai alternatif terakhir.
def _download_direct(url: str, dest: str) -> bool:
    try:
        import urllib.request
        urllib.request.urlretrieve(url, dest)
        return Path(dest).exists() and Path(dest).stat().st_size > 0
    except Exception:
        return False

# #bahasa indonesia: Menyimpan file hasil unduhan ke folder lokal
def save_locally(file_path: str, jobs: dict, job_id: str = "") -> dict:
    dest_dir  = get_local_dl_dir()
    file_name = Path(file_path).name
    dest_path = dest_dir / file_name

    # #bahasa indonesia: Hindari file yang namanya sama (tambah penomoran)
    counter = 1
    while dest_path.exists():
        stem = Path(file_name).stem
        ext  = Path(file_name).suffix
        dest_path = dest_dir / f"{stem} ({counter}){ext}"
        counter += 1

    shutil.copy2(file_path, dest_path)

    if job_id in jobs:
        jobs[job_id]["progress"] = 95
        jobs[job_id]["status_text"] = "Menyimpan file ke folder lokal..."

    return {
        "name":       dest_path.name,
        "local_path": str(dest_path),
        "folder":     str(dest_dir),
    }

# #bahasa indonesia: Berusaha menebak tipe file (MIME) berdasarkan ekstensi
def guess_mime(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {
        ".mp4": "video/mp4", ".mkv": "video/x-matroska", ".webm": "video/webm",
        ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".ogg": "audio/ogg",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".pdf": "application/pdf", ".zip": "application/zip",
    }.get(ext, "application/octet-stream")

# #bahasa indonesia: Logika utama pemanggilan yt-dlp untuk mengunduh media
async def run_yt_dlp(tmp_dir: str, url: str, job_id: str, jobs: dict):
    loop = asyncio.get_event_loop()
    output_template = os.path.join(tmp_dir, "%(title)s.%(ext)s")
    
    # Perintah standar yt-dlp
    cmd = ["yt-dlp", "--no-playlist", "-c", "--progress", "-o", output_template, url]

    jobs[job_id]["progress"]    = 10
    jobs[job_id]["status_text"] = "Mengunduh file dari sumber..."

    # Menjalankan dalam executor agar tidak menghambat event loop FastAPI
    result = await loop.run_in_executor(
        None,
        lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    )

    if result.returncode != 0:
        jobs[job_id]["status_text"] = "Mencoba unduhan langsung (fallback)..."
        filename      = url.split("/")[-1].split("?")[0] or "downloaded_file"
        fallback_path = os.path.join(tmp_dir, filename)

        fallback_result = await loop.run_in_executor(
            None,
            lambda: _download_direct(url, fallback_path)
        )
        if not fallback_result:
            raise RuntimeError(f"Gagal mengunduh. Detail error: {result.stderr[-300:]}")
    
    # Ambil file yang terunduh
    files = list(Path(tmp_dir).glob("*"))
    if not files:
        raise RuntimeError("Proses selesai tapi tidak ditemukan file hasil unduhan.")
    
    return str(files[0])
