import uuid
import json
import asyncio
import tempfile
import shutil
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from ..models.schemas import DownloadRequest
from ..core.config import LOCAL_MODE, get_local_dl_dir
from ..services.downloader import run_yt_dlp, save_locally
from ..services.drive_service import get_credentials, upload_to_drive
from .auth import sessions

router = APIRouter(prefix="/download", tags=["download"])

# #bahasa indonesia: Penyimpanan status pekerjaan unduhan real-time
jobs = {}

@router.post("")
async def download_and_upload(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Memulai proses unduhan di latar belakang."""
    if not LOCAL_MODE and not req.session_token:
        raise HTTPException(status_code=401, detail="session_token diperlukan untuk Drive mode.")

    creds = None
    if not LOCAL_MODE:
        session = sessions.get(req.session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Sesi berakhir silakan login ulang.")
        creds = get_credentials(session)

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status":      "running",
        "progress":    0,
        "status_text": "Memulai proses...",
        "result":      None,
        "error":       None,
    }

    # #bahasa indonesia: Menjalankan tugas pengunduhan di 'background_tasks' agar user tidak perlu menunggu request selesai.
    background_tasks.add_task(
        _run_download_job,
        job_id=job_id,
        creds=creds,
        url=req.url,
        folder_id=req.folder_id,
    )
    return {"job_id": job_id, "status": "started"}

@router.get("/status/{job_id}")
async def download_status_sse(job_id: str):
    """Memberikan laporan progres pengunduhan secara real-time via Server-Sent Events (SSE)."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Pekerjaan tidak ditemukan.")

    async def event_generator():
        while True:
            job = jobs.get(job_id)
            if not job:
                break

            data = json.dumps({
                "progress":    job["progress"],
                "status_text": job["status_text"],
                "status":      job["status"],
                "result":      job.get("result"),
                "error":       job.get("error"),
            })
            yield f"data: {data}\n\n"

            if job["status"] in ("done", "error"):
                await asyncio.sleep(10) # Hapus status setelah 10 detik selesai
                jobs.pop(job_id, None)
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )

# #bahasa indonesia: Logika proses pengunduhan (Latar Belakang)
async def _run_download_job(job_id: str, creds, url: str, folder_id: str):
    tmp_dir = tempfile.mkdtemp(prefix="zedd_")
    try:
        # 1. Unduh file menggunakan yt-dlp service
        file_path = await run_yt_dlp(tmp_dir, url, job_id, jobs)
        
        # 2. Simpan file (Lokal atau Drive)
        if LOCAL_MODE:
            saved = save_locally(file_path, jobs, job_id)
            jobs[job_id]["progress"]    = 100
            jobs[job_id]["status_text"] = f"Berhasil disimpan di folder lokal!"
            jobs[job_id]["status"]      = "done"
            jobs[job_id]["result"]      = {
                "file_name":  saved["name"],
                "folder":     saved["folder"],
                "local_mode": True,
            }
        else:
            jobs[job_id]["status_text"] = "Mengunggah ke Cloud Drive..."
            uploaded = upload_to_drive(creds, file_path, folder_id, jobs, job_id)
            jobs[job_id]["progress"]    = 100
            jobs[job_id]["status_text"] = "Berhasil! Tersimpan di Google Drive."
            jobs[job_id]["status"]      = "done"
            jobs[job_id]["result"]      = {
                "file_name":  uploaded.get("name"),
                "drive_link": uploaded.get("webViewLink"),
                "local_mode": False,
            }

    except Exception as e:
        jobs[job_id]["status"]      = "error"
        jobs[job_id]["status_text"] = "Terjadi kegagalan."
        jobs[job_id]["error"]       = str(e)

    finally:
        # #bahasa indonesia: Bersihkan file sementara (temporary) setelah proses selesai
        shutil.rmtree(tmp_dir, ignore_errors=True)
