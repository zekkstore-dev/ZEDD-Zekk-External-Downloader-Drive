import uuid
import urllib.parse
import base64
import hashlib
import secrets
import requests as _req
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from ..core.config import LOCAL_MODE, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, FRONTEND_URL
from ..services.drive_service import create_flow

router = APIRouter(prefix="/auth", tags=["auth"])

# #bahasa indonesia: Penyimpanan Sesi Sementara (Gunakan Redis jika untuk Produksi massal)
sessions = {}

@router.get("/login")
def auth_login():
    """Memulai alur login Google dengan tantangan keamanan PKCE (S256)."""
    if LOCAL_MODE:
        raise HTTPException(status_code=400, detail="Auth tidak diperlukan dalam LOCAL_MODE.")

    # #bahasa indonesia: Membuat kode verifikasi unik untuk keamanan tambahan (mencegah pembajakan sesi)
    code_verifier  = base64.urlsafe_b64encode(secrets.token_bytes(40)).rstrip(b'=').decode()
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()

    flow = create_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )
    
    sessions[state] = {"state": state, "code_verifier": code_verifier}
    return {"auth_url": auth_url}

@router.get("/callback")
def auth_callback(request: Request, code: str, state: str):
    """Callback dari Google setelah login berhasil."""
    if LOCAL_MODE or state not in sessions:
        raise HTTPException(status_code=400, detail="State tidak valid. Coba login ulang.")

    code_verifier = sessions[state].get("code_verifier", "")

    # #bahasa indonesia: Tukar kode dari Google dengan Token Akses (pake PKCE verifier)
    token_data = {
        "code":          code,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri":  REDIRECT_URI,
        "grant_type":    "authorization_code",
        "code_verifier": code_verifier,
    }

    token_resp = _req.post("https://oauth2.googleapis.com/token", data=token_data, timeout=15)

    if not token_resp.ok:
        raise HTTPException(status_code=502, detail="Gagal mengambil token dari Google.")

    tokens        = token_resp.json()
    access_token  = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token", "")

    # #bahasa indonesia: Ambil profil pengguna (nama & foto)
    try:
        profile = _req.get("https://www.googleapis.com/oauth2/v2/userinfo", 
                           headers={"Authorization": f"Bearer {access_token}"}, timeout=10).json()
    except Exception:
        profile = {}

    session_token = str(uuid.uuid4())
    sessions[session_token] = {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user_name":     profile.get("name", "Pengguna Google"),
        "user_email":    profile.get("email", ""),
        "user_avatar":   profile.get("picture", ""),
    }
    del sessions[state]

    # #bahasa indonesia: Alihkan kembali ke Frontend dengan token sesi
    return RedirectResponse(
        url=f"{FRONTEND_URL}?session_token={session_token}"
            f"&user_name={urllib.parse.quote(profile.get('name', ''))}"
            f"&user_avatar={urllib.parse.quote(profile.get('picture', ''))}",
    )

@router.get("/me")
def auth_me(session_token: str = ""):
    """Mengembalikan informasi pengguna yang sedang masuk."""
    if LOCAL_MODE:
        return {"user_name": "Antigravity/Local", "user_email": "local@localhost", "local_mode": True}
    
    session = sessions.get(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Sesi berakhir.")
        
    return {
        "user_name":   session["user_name"],
        "user_email":  session["user_email"],
        "user_avatar": session["user_avatar"],
        "local_mode":  False,
    }

@router.delete("/logout")
def auth_logout(session_token: str = ""):
    """Keluar dari sesi."""
    sessions.pop(session_token, None)
    return {"message": "Logout berhasil."}
