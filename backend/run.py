import uvicorn
import os
from app.core.config import LOCAL_MODE

# #bahasa indonesia: Script sederhana untuk menjalankan server backend.
if __name__ == "__main__":
    mode_str = "LOKAL (Simpan di folder)" if LOCAL_MODE else "DRIVE (Upload ke Cloud)"
    print(f"\n  🚀 ZEDD Downloader v2.0 | Mode: {mode_str}")
    print(f"  🔗 Backend berjalan di http://localhost:8000\n")
    
    # Menjalankan FastAPI dari folder app
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
