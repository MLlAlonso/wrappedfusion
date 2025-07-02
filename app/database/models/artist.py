from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    spotify_id = Column(String(255), unique=True, nullable=True)
    youtube_channel_id = Column(String(255), unique=True, nullable=True)
    image_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}', spotify_id='{self.spotify_id}')>"