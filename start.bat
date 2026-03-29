@echo off
title ZEDD - Cloud Web Downloader
color 0b
echo.
echo  =========================================
echo    ZEDD — Cloud Web Downloader v1.0
echo  =========================================
echo.

:: Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.10+ terlebih dahulu.
    pause
    exit /b 1
)

:: Masuk ke folder backend
cd /d "%~dp0backend"

:: Cek & Install FFmpeg otomatis jika tidak ada
if not exist "bin\ffmpeg.exe" (
    echo.
    echo [*] FFmpeg TIDAK ditemukan di backend\bin!
    echo [*] Mengunduh FFmpeg otomatis... (Tunggu sebentar, ukuran ~100MB)
    echo.
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal mengunduh FFmpeg. Periksa koneksi internet Anda.
        pause
        exit /b 1
    )
    echo [*] Mengekstrak FFmpeg...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'temp_ffmpeg' -Force"
    
    :: Pindahkan binary ke folder bin
    if not exist "bin" mkdir "bin"
    move /y "temp_ffmpeg\ffmpeg-master-latest-win64-gpl\bin\*" "bin\"
    
    :: Bersihkan file sementara
    del /f /q "ffmpeg.zip"
    rmdir /s /q "temp_ffmpeg"
    echo [OK] FFmpeg berhasil terpasang di backend\bin.
    echo.
)

:: Install dependencies jika belum ada
echo [*] Memeriksa dependencies Python...
pip install -r requirements.txt -q

:: Cek apakah .env sudah ada
if not exist ".env" (
    echo.
    echo [PERINGATAN] File .env belum ditemukan!
    echo [INFO] Salin .env.example menjadi .env dan isi dengan kredensial Google Anda.
    echo.
    copy .env.example .env >nul
    echo [OK] File .env telah dibuat dari template.
    echo [!] Edit file backend\.env sekarang lalu jalankan ulang skrip ini.
    echo.
    pause
    start notepad .env
    exit /b 0
)

:: Jalankan server
echo.
echo [*] Memulai Backend (FastAPI) di http://localhost:8000 ...
echo [*] Buka frontend\index.html di browser Anda (atau gunakan Live Server VSCode)
echo [*] Tekan Ctrl+C untuk menghentikan server
echo.
python run.py
pause
