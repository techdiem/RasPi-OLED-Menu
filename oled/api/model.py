from typing import Any, Optional
from pydantic import BaseModel

class NowPlayingResponse(BaseModel):
    """Response model for /nowplaying endpoint"""
    source: Optional[Any] = None
    name: Optional[str] = None
    title: Optional[str] = None
    is_playing: bool = False

class RadioStationResponse(BaseModel):
    """Response model for a single radio station"""
    id: int
    title: str
    url: str

class RadioStationCreateRequest(BaseModel):
    """Payload for creating a radio station"""
    title: str
    url: str

class RadioStationUpdateRequest(BaseModel):
    """Payload for updating a radio station"""
    title: Optional[str] = None
    url: Optional[str] = None
