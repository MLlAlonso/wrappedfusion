from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func 
from app.database.connection import Base 

class User(Base):
    """
    Modelo SQLAlchemy para la tabla 'users'.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    spotify_id = Column(String(255), unique=True, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    spotify_access_token = Column(Text, nullable=False)
    spotify_refresh_token = Column(Text, nullable=False)
    spotify_token_expires_at = Column(DateTime, nullable=False)
    google_access_token = Column(Text, nullable=False)
    google_refresh_token = Column(Text, nullable=False)
    google_token_expires_at = Column(DateTime, nullable=False)
    total_spotify_minutes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Cadena para depuración
    def __repr__(self):
        return f"<User(id={self.id}, spotify_id='{self.spotify_id}', google_id='{self.google_id}')>"