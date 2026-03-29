import os
from pathlib import Path
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
# #bahasa indonesia: Memuat konfigurasi dari file rAHASIA .env
load_dotenv()

# --- Konfigurasi Global ---
# #bahasa indonesia: Menentukan mode operasi (LOKAL atau DRIVE)
LOCAL_MODE    = os.getenv("LOCAL_MODE", "true").lower() in ("true", "1", "yes")
LOCAL_DL_DIR  = os.getenv("LOCAL_DOWNLOAD_DIR", "").strip()

# Google OAuth Credentials
CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI  = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
FRONTEND_URL  = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")

# Cakupan akses Google Drive
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

# --- FFmpeg Binaries ---
# #bahasa indonesia: Menambahkan folder bin ke PATH sistem agar FFmpeg bisa digunakan
BIN_DIR = Path(__file__).parent.parent.parent / "bin"
if BIN_DIR.exists():
    os.environ["PATH"] = str(BIN_DIR) + os.pathsep + os.environ.get("PATH", "")

def get_local_dl_dir() -> Path:
    """Mendapatkan direktori unduhan lokal. Default ke Desktop/ZEDD_DOWNLOADS."""
    if LOCAL_DL_DIR:
        p = Path(LOCAL_DL_DIR)
    else:
        desktop = Path.home() / "Desktop"
        p = desktop / "ZEDD_DOWNLOADS"
    
    p.mkdir(parents=True, exist_ok=True)
    return p
