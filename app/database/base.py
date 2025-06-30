from app.database.connection import Base

# Modelos de SQLAlchemy
from app.database.models.user import User
from app.database.models.artist import Artist
from app.database.models.track import Track, TrackArtist 
from app.database.models.spotify_play_history import SpotifyPlayHistory
from app.database.models.spotify_liked_track import SpotifyLikedTrack
from app.database.models.spotify_playlist import SpotifyPlaylist, SpotifyPlaylistTrack 
from app.database.models.user_spotify_history_summary import UserSpotifyHistorySummary