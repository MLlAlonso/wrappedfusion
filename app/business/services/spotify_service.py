import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings
from app.database.models.user import User

class SpotifyService:
    """
    Servicio para interactuar con la API de Spotify.
    """
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _refresh_access_token(self) -> bool:
        """
        Refresca el token de acceso de Spotify si ha expirado.
        """
        if not self.user.spotify_refresh_token:
            print(f"DEBUG: No hay refresh token para el usuario {self.user.id}.")
            return False

        if self.user.spotify_token_expires_at and \
           self.user.spotify_token_expires_at > datetime.utcnow() + timedelta(minutes=5):
            print(f"DEBUG: Token de acceso de Spotify aún válido para el usuario {self.user.id}. No se requiere refresco.")
            return True

        print(f"DEBUG: Refrescando token de acceso de Spotify para el usuario {self.user.id}...")
        token_request_body = {
            "grant_type": "refresh_token",
            "refresh_token": self.user.spotify_refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET
        }

        try:
            response = await self.client.post(
                self.SPOTIFY_TOKEN_URL,
                data=token_request_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()

            self.user.spotify_access_token = token_data["access_token"]
            self.user.spotify_token_expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            if "refresh_token" in token_data:
                self.user.spotify_refresh_token = token_data["refresh_token"]
            self.user.updated_at = datetime.utcnow()

            self.db.add(self.user)
            self.db.commit()
            self.db.refresh(self.user)
            print(f"DEBUG: Token de acceso de Spotify refrescado con éxito para el usuario {self.user.id}.")
            return True
        except httpx.HTTPStatusError as e:
            print(f"ERROR: Fallo al refrescar token de Spotify para el usuario {self.user.id}: {e.response.text}")
            raise Exception(f"Error al refrescar token de Spotify: {e.response.text}")
        except httpx.RequestError as e:
            print(f"ERROR: Error de red al refrescar token de Spotify para el usuario {self.user.id}: {e}")
            raise Exception(f"Error de red al refrescar token de Spotify: {e}")
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"ERROR: Error de DB al guardar token refrescado para el usuario {self.user.id}: {e}")
            raise Exception(f"Error de DB al guardar token refrescado: {e}")

    async def _get_api_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Método genérico para realizar llamadas a la API de Spotify.
        Asegura que el token de acceso esté refrescado antes de cada llamada.
        """
        if not await self._refresh_access_token():
            raise Exception("No se pudo refrescar/obtener un token de acceso válido para Spotify.")

        headers = {
            "Authorization": f"Bearer {self.user.spotify_access_token}",
            "Content-Type": "application/json"
        }
        url = f"{self.SPOTIFY_API_BASE_URL}{endpoint}"
        print(f"DEBUG: Llamando a Spotify API: {url} con params: {params}")
        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"ERROR: Error HTTP al obtener datos de Spotify ({endpoint}): {e.response.status_code} - {e.response.text}")
            raise Exception(f"Error al obtener datos de Spotify: {e.response.text}")
        except httpx.RequestError as e:
            print(f"ERROR: Error de red al obtener datos de Spotify ({endpoint}): {e}")
            raise Exception(f"Error de red al obtener datos de Spotify: {e}")

    async def get_spotify_profile(self) -> Dict[str, Any]:
        """
        Obtiene el perfil del usuario de Spotify.
        """
        return await self._get_api_data("/me")

    async def get_recently_played_tracks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene las canciones reproducidas recientemente por el usuario de Spotify.
        """
        data = await self._get_api_data("/me/player/recently-played", params={"limit": limit})
        for item in data.get("items", []):
            if item.get("track") and item["track"].get("album") and item["track"]["album"].get("images"):
                images = item["track"]["album"]["images"]
                if images:
                    item["track"]["album_image_url"] = images[0]["url"]
        return data.get("items", [])

    async def get_user_liked_tracks(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Obtiene las canciones que el usuario ha guardado en su biblioteca.
        """
        data = await self._get_api_data("/me/tracks", params={"limit": limit, "offset": offset})
        # Añadir lógica para obtener la mejor imagen de portada
        for item in data.get("items", []):
            if item.get("track") and item["track"].get("album") and item["track"]["album"].get("images"):
                images = item["track"]["album"]["images"]
                if images:
                    item["track"]["album_image_url"] = images[0]["url"]
        return data

    async def get_user_top_items(self, item_type: str, limit: int = 5, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """
        Obtiene los top artistas o canciones del usuario.
        """
        data = await self._get_api_data(f"/me/top/{item_type}", params={"limit": limit, "time_range": time_range})
        items = data.get("items", [])
        
        if item_type == 'artists':
            for artist_data in items:
                if artist_data.get("images"):
                    images = artist_data["images"]
                    if images:
                        artist_data["image_url"] = images[0]["url"]
        elif item_type == 'tracks':
            for track_data in items:
                if track_data.get("album") and track_data["album"].get("images"):
                    images = track_data["album"]["images"]
                    if images:
                        track_data["album_image_url"] = images[0]["url"] 
        return items

    async def get_user_playlists(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Obtiene las playlists del usuario.
        """
        return await self._get_api_data("/me/playlists", params={"limit": limit, "offset": offset})

    async def get_playlist_items(self, playlist_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Obtiene los ítems (tracks) de una playlist específica.
        """
        data = await self._get_api_data(f"/playlists/{playlist_id}/tracks", params={"limit": limit, "offset": offset})
        return data

    async def get_track_details(self, track_id: str) -> Dict[str, Any]:
        return await self._get_api_data(f"/tracks/{track_id}")

    async def get_artist_details(self, artist_id: str) -> Dict[str, Any]:
        return await self._get_api_data(f"/artists/{artist_id}")