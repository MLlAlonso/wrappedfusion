from fastapi import APIRouter, HTTPException, Depends, status
from starlette.responses import JSONResponse, RedirectResponse
import httpx
import base64
import hashlib
import secrets
import urllib.parse
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings
from app.database.connection import get_db
from app.database.models.user import User

router = APIRouter()

# --- Configuración de Spotify ---
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

# OAuth 2.0 Scopes para Spotify
SPOTIFY_SCOPES = [
    "user-read-private",
    "user-read-email",
    "user-read-recently-played",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-top-read"
]

class SpotifyCallbackRequest(BaseModel):
    code: str
    code_verifier: str
    state: Optional[str] = None

def generate_pkce_challenge(length: int = 128):
    code_verifier = secrets.token_urlsafe(length)
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge

# Endpoint para iniciar el flujo de autenticación de Spotify
@router.get("/auth/spotify", summary="Iniciar autenticación con Spotify (desde la UI del servicio)")
async def spotify_auth_init_from_ui():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "El flujo de autenticación de Spotify se inicia desde el frontend de este servicio."}
    )

# Endpoint para manejar el callback de Spotify desde el frontend
@router.post("/auth/spotify/callback", summary="Manejar callback de autenticación de Spotify")
async def spotify_callback(
    request_data: SpotifyCallbackRequest,
    db: Session = Depends(get_db),
):
    code = request_data.code
    code_verifier = request_data.code_verifier

    client_credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()
    auth_headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_request_body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient() as client:
        try:
            # Primera solicitud: Intercambio de tokens
            response = await client.post(
                SPOTIFY_TOKEN_URL,
                data=token_request_body,
                headers=auth_headers
            )
            response.raise_for_status()
            token_data = response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            print(f"ERROR: Fallo al obtener tokens de Spotify: {error_detail}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error al obtener tokens de Spotify: {error_detail}"
            )
        except httpx.RequestError as e:
            print(f"ERROR: Error de red al conectar con Spotify: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error de red al conectar con Spotify: {e}"
            )

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")

        if not access_token or not refresh_token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se recibieron tokens válidos de Spotify.")

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Segunda solicitud: Obtener información del usuario
        try:
            user_info_response = await client.get(
                f"{SPOTIFY_API_BASE_URL}/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            spotify_user_data = user_info_response.json()
            spotify_id = spotify_user_data.get("id")
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            print(f"ERROR: Error al obtener info de usuario de Spotify: {error_detail}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error al obtener info de usuario de Spotify: {error_detail}"
            )

    # Try-except para operaciones de base de datos
    try:
        if not spotify_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo obtener el ID de usuario de Spotify.")

        user = db.query(User).filter(User.spotify_id == spotify_id).first()

        if user:
            user.spotify_access_token = access_token
            user.spotify_refresh_token = refresh_token
            user.spotify_token_expires_at = expires_at
            user.updated_at = datetime.utcnow()
        else:
            new_user = User(
                spotify_id=spotify_id,
                spotify_access_token=access_token,
                spotify_refresh_token=refresh_token,
                spotify_token_expires_at=expires_at,
                google_access_token="",
                google_refresh_token="",
                google_token_expires_at=datetime.utcnow()
            )
            db.add(new_user)

        db.commit()
        if not user:
            db.refresh(new_user)
            user_id = new_user.id
        else:
            user_id = user.id

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Autenticación de Spotify exitosa y tokens guardados.",
                "user_id": user_id,
                "spotify_id": spotify_id
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR: Error de DB al guardar/actualizar usuario de Spotify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos durante la autenticación: {e}"
        )
    except Exception as e:
        db.rollback()
        print(f"ERROR: Error inesperado en spotify_callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno inesperado durante la autenticación: {e}"
        )