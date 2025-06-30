from pydantic import BaseModel
from typing import List, Optional

# Datos de Spotify que se enviarán al frontend

class TrackStat(BaseModel):
    title: str
    play_count: int

class ArtistStat(BaseModel):
    name: str
    play_count: int

class LikedTrack(BaseModel):
    title: str

class SpotifyStatsResponse(BaseModel):
    total_spotify_minutes: int
    top_10_tracks: List[TrackStat]
    top_5_artists: List[ArtistStat]
    liked_tracks: List[LikedTrack]
    playlists: List[str] 

    class Config:
        from_attributes = True