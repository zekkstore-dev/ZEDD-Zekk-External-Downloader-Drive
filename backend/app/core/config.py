# ───────────────────────────────────────────────────────────────
#  ZEDD - Backend Configuration
# ───────────────────────────────────────────────────────────────
import os
from pathlib import Path
from dotenv import load_dotenv

# Ambil path root proyek
BASE_DIR = Path(__file__).parent.parent.parent

# Load file .env (Pastikan file ini ada di folder backend/)
load_dotenv(BASE_DIR / ".env")

# Konfigurasi Google Drive
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")

# Pengaturan Unduhan
# Jika True, file disimpan di Desktop. Jika False, diupload ke Drive.
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"

# Folder sementara untuk proses download
DOWNLOAD_TEMP_DIR = BASE_DIR / "tmp"
DOWNLOAD_TEMP_DIR.mkdir(exist_ok=True)

# Path FFmpeg (Jika ada di folder bin lokal)
BIN_DIR = BASE_DIR / "bin"
if BIN_DIR.exists():
    os.environ["PATH"] += os.pathsep + str(BIN_DIR.absolute())

# Pesan Logika dalam Bahasa Indonesia:
# Memastikan semua variabel lingkungan dimuat dengan benar sebelum aplikasi dijalankan.
