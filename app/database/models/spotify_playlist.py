from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base 

# Tabla de unión para la relación muchos a muchos entre SpotifyPlaylist y Track
class SpotifyPlaylistTrack(Base):
    """
    Relaciona playlists de Spotify con tracks.
    """
    __tablename__ = "spotify_playlist_tracks"
    playlist_id = Column(Integer, ForeignKey("spotify_playlists.id"), primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    added_at = Column(DateTime, nullable=True)
    def __repr__(self):
        return f"<SpotifyPlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id})>"

class SpotifyPlaylist(Base):
    """
    Almacena información sobre las playlists de Spotify de un usuario.
    """
    __tablename__ = "spotify_playlists"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    playlist_name = Column(String(255), nullable=False)
    spotify_playlist_id = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    total_tracks = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", backref="spotify_playlists")
    tracks = relationship("Track", secondary="spotify_playlist_tracks", backref="spotify_playlists")

    def __repr__(self):
        return f"<SpotifyPlaylist(id={self.id}, name='{self.playlist_name}', spotify_id='{self.spotify_playlist_id}')>"