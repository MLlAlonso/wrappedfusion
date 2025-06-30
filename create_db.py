import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.connection import create_db_tables
from app.database.models.user import User
from app.database.models.artist import Artist
from app.database.models.track import Track, TrackArtist 
from app.database.models.spotify_play_history import SpotifyPlayHistory
from app.database.models.spotify_liked_track import SpotifyLikedTrack
from app.database.models.spotify_playlist import SpotifyPlaylist, SpotifyPlaylistTrack 
from app.database.models.user_spotify_history_summary import UserSpotifyHistorySummary

if __name__ == "__main__":
    print("Intentando crear tablas de la base de datos...")
    create_db_tables()
    print("Proceso de creación de tablas finalizado.")