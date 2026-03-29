from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, download
from .core.config import FRONTEND_URL, LOCAL_MODE

# #bahasa indonesia: Inisialisasi utama aplikasi FastAPI (Mesin Backend)
app = FastAPI(
    title="ZEDD Downloader API", 
    description="Layanan pengunduh media eksternal ke Cloud Drive atau folder lokal.",
    version="2.0.0"
)

# #bahasa indonesia: Konfigurasi CORS (Cross-Origin Resource Sharing)
# Mengizinkan Frontend untuk mengakses API Backend meskipun berjalan di domain/port yang berbeda.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# #bahasa indonesia: Menghubungkan modul Route ke aplikasi inti
app.include_router(auth.router)
app.include_router(download.router)

@app.get("/")
def read_root():
    """Beranda API ZEDD."""
    return {
        "status":     "online",
        "message":    "API ZEDD Downloader siap digunakan!",
        "version":    "2.0.0",
        "local_mode": LOCAL_MODE,
    }

@app.get("/health")
def health_check():
    """Beranda Health Check."""
    return {"status": "ok"}

@app.get("/mode")
def get_mode():
    """Mendapatkan informasi mode saat ini (DRIVE atau LOCAL)."""
    return {"local_mode": LOCAL_MODE}
