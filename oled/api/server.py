"""FastAPI server for OLED menu REST endpoints"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

app = FastAPI(title="RasPi OLED Menu API", version="1.0.0")


class NowPlayingResponse(BaseModel):
    """Response model for /nowplaying endpoint"""
    source: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
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


class APIStateManager:
    """Manages API state via EventBus subscriptions"""

    def __init__(self, eventbus=None, mopidy=None):
        self.eventbus = eventbus
        self.mopidy = mopidy
        self.state = {
            "source": None,
            "title": None,
            "artist": None,
            "is_playing": False
        }

        if self.eventbus is not None:
            self.eventbus.subscribe("music.nowplaying", self._on_nowplaying)
            self.eventbus.subscribe("music.playstate", self._on_playstate)
            self.eventbus.subscribe("music.source", self._on_source)

    def _on_nowplaying(self, playing):
        if playing is None:
            return
        self.state["title"] = playing.get("title", "")
        self.state["artist"] = playing.get("artist", "")

    def _on_playstate(self, playstate):
        if playstate is None:
            return
        self.state["is_playing"] = playstate == "play"
        if not self.state["is_playing"]:
            self.state["title"] = None
            self.state["artist"] = None

    def _on_source(self, source):
        if source is None:
            return
        self.state["source"] = source

    def get_state(self) -> NowPlayingResponse:
        return NowPlayingResponse(**self.state)

    def get_radiostations(self) -> List[RadioStationResponse]:
        if self.mopidy is None:
            return []

        return [
            RadioStationResponse(id=index, **station)
            for index, station in enumerate(self.mopidy.get_radiostations())
        ]

    def add_radiostation(self, title, url) -> RadioStationResponse:
        self._require_mopidy()
        station_id, station = self.mopidy.add_radiostation(title, url)
        return RadioStationResponse(id=station_id, **station)

    def update_radiostation(self, station_id, title=None, url=None) -> RadioStationResponse:
        self._require_mopidy()
        try:
            station = self.mopidy.update_radiostation(station_id, title=title, url=url)
        except IndexError as exc:
            raise HTTPException(status_code=404, detail="Radio station not found") from exc
        return RadioStationResponse(id=station_id, **station)

    def delete_radiostation(self, station_id) -> RadioStationResponse:
        self._require_mopidy()
        try:
            station = self.mopidy.delete_radiostation(station_id)
        except IndexError as exc:
            raise HTTPException(status_code=404, detail="Radio station not found") from exc
        return RadioStationResponse(id=station_id, **station)

    def _require_mopidy(self):
        if self.mopidy is None:
            raise HTTPException(status_code=503, detail="Mopidy control is not available")


# Global state manager - initialized from oled.py
# Using a dict to allow late assignment from init_api_manager() without needing 'global' keyword
_api_manager = {"instance": APIStateManager()}


def _get_api_manager():
    return _api_manager["instance"]

# ----------------------------
# FastAPI endpoint definitions

@app.get("/nowplaying", response_model=NowPlayingResponse)
async def get_nowplaying():
    return _get_api_manager().get_state()


@app.get("/radiostations", response_model=List[RadioStationResponse])
async def get_radiostations():
    return _get_api_manager().get_radiostations()


@app.post("/radiostations", response_model=RadioStationResponse, status_code=201)
async def create_radiostation(station: RadioStationCreateRequest):
    try:
        return _get_api_manager().add_radiostation(station.title, station.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.patch("/radiostations/{station_id}", response_model=RadioStationResponse)
async def patch_radiostation(
    station_id: int = Path(..., ge=0),
    station: Optional[RadioStationUpdateRequest] = None
):
    if station is None:
        raise HTTPException(status_code=400, detail="Request body is required")
    try:
        return _get_api_manager().update_radiostation(station_id,
                                                      title=station.title, url=station.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/radiostations/{station_id}", response_model=RadioStationResponse)
async def delete_radiostation(station_id: int = Path(..., ge=0)):
    """Delete a radio station entry"""
    return _get_api_manager().delete_radiostation(station_id)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


def init_api_manager(eventbus, mopidy=None):
    _api_manager["instance"] = APIStateManager(eventbus, mopidy)
