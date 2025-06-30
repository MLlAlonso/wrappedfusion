from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base 
from sqlalchemy.dialects.mysql import JSON 

class UserSpotifyHistorySummary(Base):
    """
    Almacena un resumen del historial de reproducción de Spotify del usuario,
    incluyendo la lista de IDs de las últimas canciones sincronizadas para
    el cálculo de minutos acumulados.
    """
    __tablename__ = "user_spotify_history_summary"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    last_synced_track_ids = Column(JSON, nullable=False, default="[]") # Almacena los IDs de los últimos tracks sincronizados para evitar duplicados en el cálculo de minutos
    total_minutes_listened = Column(BigInteger, default=0, nullable=False) 
    last_sync_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="spotify_summary")
    def __repr__(self):
        return (f"<UserSpotifyHistorySummary(user_id={self.user_id}, "
                f"total_minutes={self.total_minutes_listened})>")