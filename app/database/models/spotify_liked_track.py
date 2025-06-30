from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base 

class SpotifyLikedTrack(Base):
    """
    Almacena canciones marcadas como "Me gusta"/"Favoritas" en Spotify.
    """
    __tablename__ = "spotify_liked_tracks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False) 
    added_at = Column(DateTime, nullable=False, server_default=func.now()) 
    platform_track_id = Column(String(255), nullable=False) 

    # Asegura que un usuario no pueda tener la misma canción "liked" dos veces
    __table_args__ = (UniqueConstraint("user_id", "track_id", name="uq_spotify_liked_track"),)
    user = relationship("User", backref="spotify_liked_tracks")
    track = relationship("Track", backref="spotify_liked_tracks")

    def __repr__(self):
        return f"<SpotifyLikedTrack(user_id={self.user_id}, track_id={self.track_id})>"