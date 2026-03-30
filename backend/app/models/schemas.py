from pydantic import BaseModel
from typing import Optional

class DownloadRequest(BaseModel):
    url: str
    filename: Optional[str] = None

# Komentar Bahasa Indonesia:
# Skema data untuk memvalidasi input dari user saat melakukan request download.
