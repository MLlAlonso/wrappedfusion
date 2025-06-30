from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models.user import User
from app.database.models.track import Track, TrackArtist
from app.database.models.artist import Artist
from app.database.models.spotify_play_history import SpotifyPlayHistory
from app.database.models.spotify_liked_track import SpotifyLikedTrack
from app.database.models.spotify_playlist import SpotifyPlaylist, SpotifyPlaylistTrack
from app.database.models.user_spotify_history_summary import UserSpotifyHistorySummary
from app.business.services.spotify_service import SpotifyService

router = APIRouter()

async def get_or_create_artist(db: Session, artist_data: Dict[str, Any]) -> Artist:
    """
    Busca un artista por spotify_id o nombre. Si no existe, lo crea.
    """
    spotify_id = artist_data.get("id")
    artist_name = artist_data.get("name")

    artist = None
    if spotify_id:
        artist = db.query(Artist).filter(Artist.spotify_id == spotify_id).first()
    
    if not artist and artist_name:
        artist = db.query(Artist).filter(Artist.name == artist_name).first()

    if not artist:
        artist = Artist(name=artist_name, spotify_id=spotify_id)
        db.add(artist)
        db.flush() # Asegura que el ID del nuevo artista esté disponible
        print(f"DEBUG: Nuevo artista creado: {artist_name} (Spotify ID: {spotify_id})")
    else:
        if not artist.spotify_id and spotify_id:
            artist.spotify_id = spotify_id
            db.add(artist)
        print(f"DEBUG: Artista existente encontrado: {artist_name} (ID: {artist.id})")
    
    return artist

async def get_or_create_track(db: Session, track_data: Dict[str, Any]) -> Track:
    """
    Busca un track por spotify_id o ISRC. Si no existe, lo crea.
    """
    spotify_id = track_data.get("id")
    track_title = track_data.get("name")
    duration_ms = track_data.get("duration_ms")
    isrc = track_data.get("external_ids", {}).get("isrc")

    track = None
    if spotify_id:
        track = db.query(Track).filter(Track.spotify_id == spotify_id).first()
    
    if not track and isrc:
        track = db.query(Track).filter(Track.isrc == isrc).first()

    if not track:
        track = Track(
            title=track_title,
            duration_ms=duration_ms,
            isrc=isrc,
            spotify_id=spotify_id
        )
        db.add(track)
        db.flush()
        print(f"DEBUG: Nuevo track creado: {track_title} (Spotify ID: {spotify_id})")
    else:
        if not track.spotify_id and spotify_id:
            track.spotify_id = spotify_id
        if not track.isrc and isrc:
            track.isrc = isrc
        if not track.duration_ms and duration_ms:
            track.duration_ms = duration_ms
        db.add(track)
        print(f"DEBUG: Track existente encontrado: {track_title} (ID: {track.id})")

    processed_artist_ids = set()
    if "artists" in track_data and track_data["artists"]:
        for artist_data in track_data["artists"]:
            artist_spotify_id = artist_data.get("id")
            if artist_spotify_id:
                if artist_spotify_id in processed_artist_ids:
                    print(f"DEBUG: Artista {artist_data.get('name')} (ID: {artist_spotify_id}) ya procesado para este track. Saltando.")
                    continue
                processed_artist_ids.add(artist_spotify_id)

            artist = await get_or_create_artist(db, artist_data)
            
            existing_association = db.query(TrackArtist).filter_by(
                track_id=track.id, 
                artist_id=artist.id
            ).first()

            if not existing_association:
                track_artist = TrackArtist(track_id=track.id, artist_id=artist.id)
                db.add(track_artist)
                print(f"DEBUG: Asociando track {track.id} con artista {artist.id}")
            else:
                print(f"DEBUG: Relación track {track.id} - artista {artist.id} ya existe.")
    
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR: Fallo al commitear track/artista: {e}")
        raise

    return track


@router.post("/spotify/sync_data/{user_id}", summary="Sincronizar datos de Spotify para un usuario")
async def sync_spotify_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    async with SpotifyService(db, user) as spotify_service:
        try:
            # --- 1. Sincronizar Historial de Reproducción ---
            print(f"DEBUG: Sincronizando historial de reproducción de Spotify para el usuario {user_id}...")
            recently_played = await spotify_service.get_recently_played_tracks(limit=50)

            user_summary = db.query(UserSpotifyHistorySummary).filter_by(user_id=user_id).first()
            if not user_summary:
                user_summary = UserSpotifyHistorySummary(user_id=user_id, last_synced_track_ids=json.dumps([]))
                db.add(user_summary)
                db.flush()
            
            last_synced_ids = set(json.loads(user_summary.last_synced_track_ids))
            newly_processed_track_ids = []
            
            total_minutes_added_this_sync = 0

            for item in reversed(recently_played):
                track_data = item.get("track")
                played_at_str = item.get("played_at")
                
                if not track_data or not played_at_str:
                    continue

                spotify_track_id = track_data.get("id")
                
                unique_play_identifier = f"{spotify_track_id}_{played_at_str}"
                
                if unique_play_identifier not in last_synced_ids:
                    track = await get_or_create_track(db, track_data)
                    
                    play_history_entry = SpotifyPlayHistory(
                        user_id=user_id,
                        track_id=track.id,
                        played_at=datetime.fromisoformat(played_at_str.replace("Z", "+00:00")),
                        platform_track_id=spotify_track_id,
                        platform_artist_id=track_data['artists'][0]['id'] if track_data['artists'] else '',
                        duration_ms=track.duration_ms or 0
                    )
                    db.add(play_history_entry)
                    
                    total_minutes_added_this_sync += (track.duration_ms or 0) / 60000
                    print(f"DEBUG: Añadiendo {track.title} ({track.duration_ms/60000:.2f} min). Total añadido: {total_minutes_added_this_sync:.2f} min.")
                
                newly_processed_track_ids.append(unique_play_identifier)


            user_summary.last_synced_track_ids = json.dumps(newly_processed_track_ids[-50:])
            user_summary.total_minutes_listened += int(total_minutes_added_this_sync)
            user_summary.last_sync_at = datetime.utcnow()
            db.add(user_summary)
            
            user.total_spotify_minutes = user_summary.total_minutes_listened
            db.add(user)

            db.commit()

            print(f"DEBUG: Sincronización de historial de Spotify completada para el usuario {user_id}. Minutos añadidos: {total_minutes_added_this_sync:.2f}")

            # --- Sincronizar Canciones Favoritas (Liked Tracks) ---
            print(f"DEBUG: Sincronizando canciones favoritas de Spotify para el usuario {user_id}...")
            liked_tracks_data = await spotify_service.get_user_liked_tracks(limit=50)
            for item in liked_tracks_data.get("items", []):
                track_data = item.get("track")
                if not track_data: continue

                track = await get_or_create_track(db, track_data)
                
                existing_liked = db.query(SpotifyLikedTrack).filter_by(
                    user_id=user_id,
                    track_id=track.id
                ).first()

                if not existing_liked:
                    liked_entry = SpotifyLikedTrack(
                        user_id=user_id,
                        track_id=track.id,
                        added_at=datetime.fromisoformat(item.get("added_at").replace("Z", "+00:00")) if item.get("added_at") else datetime.utcnow(),
                        platform_track_id=track_data.get("id")
                    )
                    db.add(liked_entry)
                    print(f"DEBUG: Añadida canción favorita: {track.title}")
            db.commit()

            # --- Sincronizar Playlists ---
            print(f"DEBUG: Sincronizando playlists de Spotify para el usuario {user_id}...")
            playlists_data = await spotify_service.get_user_playlists(limit=50) # Obtener las primeras 50 playlists
            for playlist_item in playlists_data.get("items", []):
                spotify_playlist_id = playlist_item.get("id")
                playlist_name = playlist_item.get("name")
                description = playlist_item.get("description")
                is_public = playlist_item.get("public")
                total_tracks = playlist_item.get("tracks", {}).get("total") 

                # Buscar playlist existente o crear una nueva
                existing_playlist = db.query(SpotifyPlaylist).filter_by(
                    user_id=user_id,
                    spotify_playlist_id=spotify_playlist_id
                ).first()

                if not existing_playlist:
                    playlist_entry = SpotifyPlaylist(
                        user_id=user_id,
                        playlist_name=playlist_name,
                        spotify_playlist_id=spotify_playlist_id,
                        description=description,
                        is_public=is_public,
                        total_tracks=total_tracks
                    )
                    db.add(playlist_entry)
                    db.flush()
                    print(f"DEBUG: Añadida playlist: {playlist_name}")
                else:
                    # Actualizar la playlist 
                    existing_playlist.playlist_name = playlist_name
                    existing_playlist.description = description
                    existing_playlist.is_public = is_public
                    existing_playlist.total_tracks = total_tracks
                    db.add(existing_playlist) 
                    playlist_entry = existing_playlist 
                    print(f"DEBUG: Actualizada playlist: {playlist_name}")
            db.commit() 

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Datos de Spotify sincronizados con éxito.", "user_id": user_id}
            )

        except Exception as e:
            db.rollback()
            print(f"ERROR: Fallo en la sincronización de datos de Spotify para el usuario {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo en la sincronización de datos de Spotify: {e}"
            )

@router.get("/spotify/stats/{user_id}", summary="Obtener estadísticas de Spotify para un usuario")
async def get_spotify_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las estadísticas procesadas de Spotify para un usuario.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    # Minutos escuchados totales
    user_summary = db.query(UserSpotifyHistorySummary).filter_by(user_id=user_id).first()
    total_spotify_minutes = user_summary.total_minutes_listened if user_summary else 0

    # Top 10 Canciones
    top_tracks_query = (
        db.query(Track.title, Track.id, func.count(SpotifyPlayHistory.track_id).label("play_count"))
        .join(SpotifyPlayHistory, SpotifyPlayHistory.track_id == Track.id)
        .filter(SpotifyPlayHistory.user_id == user_id)
        .group_by(Track.title, Track.id)
        .order_by(func.count(SpotifyPlayHistory.track_id).desc())
        .limit(10)
        .all()
    )
    top_tracks_spotify = [
        {"title": track.title, "play_count": track.play_count} for track in top_tracks_query
    ]

    # Top 5 Artistas (de historial de reproducción)
    top_artists_query = (
        db.query(Artist.name, Artist.id, func.count(SpotifyPlayHistory.platform_artist_id).label("play_count"))
        .join(TrackArtist, TrackArtist.track_id == SpotifyPlayHistory.track_id)
        .join(Artist, Artist.id == TrackArtist.artist_id)
        .filter(SpotifyPlayHistory.user_id == user_id)
        .group_by(Artist.name, Artist.id)
        .order_by(func.count(SpotifyPlayHistory.platform_artist_id).desc())
        .limit(5)
        .all()
    )
    top_artists_spotify = [
        {"name": artist.name, "play_count": artist.play_count} for artist in top_artists_query
    ]

    # Canciones Favoritas (de historial de reproducción)
    liked_tracks_query = (
        db.query(Track.title, Track.id)
        .join(SpotifyLikedTrack, SpotifyLikedTrack.track_id == Track.id)
        .filter(SpotifyLikedTrack.user_id == user_id)
        .order_by(SpotifyLikedTrack.added_at.desc())
        .limit(10)
        .all()
    )
    liked_tracks_spotify = [
        {"title": track.title} for track in liked_tracks_query
    ]

    # Playlists (solo nombres por ahora)
    playlists_query = (
        db.query(SpotifyPlaylist.playlist_name)
        .filter(SpotifyPlaylist.user_id == user_id)
        .order_by(SpotifyPlaylist.playlist_name)
        .all()
    )
    playlists_spotify = [p.playlist_name for p in playlists_query]


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "total_spotify_minutes": total_spotify_minutes,
            "top_10_tracks": top_tracks_spotify,
            "top_5_artists": top_artists_spotify,
            "liked_tracks": liked_tracks_spotify,
            "playlists": playlists_spotify
        }
    )