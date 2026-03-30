from fastapi import APIRouter, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
import asyncio
import os
from ..models.schemas import DownloadRequest
from ..services.downloader import run_download
from ..services.drive_service import upload_to_drive
from ..core.config import DOWNLOAD_TEMP_DIR, LOCAL_MODE

router = APIRouter(prefix="/download", tags=["Download"])

# Simulasi status progres (untuk demo sederhana)
progress_store = {}

@router.post("/")
async def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    job_id = str(hash(req.url))
    progress_store[job_id] = "Starting..."
    
    # Jalankan proses download di background agar tidak memblokir server
    background_tasks.add_task(process_job, job_id, req)
    return {"job_id": job_id}

async def process_job(job_id: str, req: DownloadRequest):
    # Logika alur: Download -> (Optional) Upload -> Delete Temp
    file_path = os.path.join(DOWNLOAD_TEMP_DIR, f"{job_id}.mp4")
    
    pernah_berhasil = run_download(req.url, file_path)
    if pernah_berhasil:
        progress_store[job_id] = "Uploading to Drive..."
        # Jika bukan Local Mode, upload ke Drive (creds perlu dipassing dari frontend via req header/body)
        progress_store[job_id] = "Done"
    else:
        progress_store[job_id] = "Error"

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    return {"status": progress_store.get(job_id, "Unknown")}
