from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, download

app = FastAPI(title="ZEDD API", version="2.0")

# Izinkan CORS agar frontend bisa memanggil backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router
app.include_router(auth.router)
app.include_router(download.router)

@app.get("/")
async def root():
    return {"message": "ZEDD Backend MVC is Running!"}

# Komentar Bahasa Indonesia:
# File ini adalah pusat dari aplikasi backend yang menghubungkan semua route.
