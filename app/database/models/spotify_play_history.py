from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base 

class SpotifyPlayHistory(Base):
    """
    Almacena el historial de reproducciones de Spotify.
    """
    __tablename__ = "spotify_play_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    played_at = Column(DateTime, nullable=False, index=True) 
    platform_track_id = Column(String(255), nullable=False) 
    platform_artist_id = Column(String(255), nullable=False) 
    duration_ms = Column(Integer, nullable=False) 

    user = relationship("User", backref="spotify_play_history")
    track = relationship("Track", backref="spotify_play_history")

    def __repr__(self):
        return f"<SpotifyPlayHistory(user_id={self.user_id}, track_id={self.track_id}, played_at='{self.played_at}')>"