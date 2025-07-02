from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class TrackArtist(Base):
    __tablename__ = "track_artists"
    track_id = Column(Integer, ForeignKey("tracks.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), primary_key=True)

    def __repr__(self):
        return f"<TrackArtist(track_id={self.track_id}, artist_id={self.artist_id})>"

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    duration_ms = Column(Integer, nullable=True)
    isrc = Column(String(12), unique=True, nullable=True)
    spotify_id = Column(String(255), unique=True, nullable=True)
    youtube_id = Column(String(255), unique=True, nullable=True)
    album_image_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    artists = relationship("Artist", secondary="track_artists", backref="tracks")

    def __repr__(self):
        return f"<Track(id={self.id}, title='{self.title}', spotify_id='{self.spotify_id}')>"