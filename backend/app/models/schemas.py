from pydantic import BaseModel

# #bahasa indonesia: Model data untuk request pengunduhan
class DownloadRequest(BaseModel):
    url: str
    folder_id: str = ""
    session_token: str = ""   # Kosong jika LOCAL_MODE=true
