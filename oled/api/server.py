"""FastAPI server for OLED menu REST endpoints"""
import asyncio
from pathlib import Path
from typing import Any, List, Optional
from fastapi import FastAPI, HTTPException, Path as FastAPIPath, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="RasPi OLED Menu API", version="1.0.0")


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


class NowPlayingSocketHub:
    """Keeps websocket clients for now playing updates in sync."""

    def __init__(self):
        self.connections = set()
        self.loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if self.loop is None:
            self.loop = asyncio.get_running_loop()
        self.connections.add(websocket)

    def broadcast_threadsafe(self, state: NowPlayingResponse):
        if self.loop is None:
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(state), self.loop)

    async def broadcast(self, state: NowPlayingResponse):
        payload = state.model_dump()
        closed_connections = []
        for websocket in self.connections.copy():
            try:
                await websocket.send_json(payload)
            except Exception:
                closed_connections.append(websocket)
        for websocket in closed_connections:
            self.connections.discard(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)


class APIStateManager:
    """Manages API state via EventBus subscriptions"""

    def __init__(self, eventbus=None, mopidy=None, nowplaying_hub=None):
        self.eventbus = eventbus
        self.mopidy = mopidy
        self.nowplaying_hub = nowplaying_hub
        self.state = {
            "source": None,
            "name": None,
            "title": None,
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
        self.state["name"] = playing.get("name", "")
        source = playing.get("source")
        if source:
            self.state["source"] = source
        self._broadcast_nowplaying_state()

    def _on_playstate(self, playstate):
        if playstate is None:
            return
        self.state["is_playing"] = playstate == "play"
        if not self.state["is_playing"]:
            self.state["title"] = None
            self.state["name"] = None
        self._broadcast_nowplaying_state()

    def _on_source(self, source):
        if source is None:
            return
        self.state["source"] = source
        self._broadcast_nowplaying_state()

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

    def play_radiostation(self, station_id) -> RadioStationResponse:
        self._require_mopidy()
        stations = self.mopidy.get_radiostations()
        if station_id < 0 or station_id >= len(stations):
            raise HTTPException(status_code=404, detail="Radio station not found")
        self.mopidy.playradiostation(station_id)
        station = stations[station_id]
        return RadioStationResponse(id=station_id, **station)

    def _require_mopidy(self):
        if self.mopidy is None:
            raise HTTPException(status_code=503, detail="Mopidy control is not available")

    def _broadcast_nowplaying_state(self):
        if self.nowplaying_hub is None:
            return
        self.nowplaying_hub.broadcast_threadsafe(self.get_state())


# Global state manager - initialized from oled.py
# Using a dict to allow late assignment from init_api_manager() without needing 'global' keyword
_nowplaying_hub = NowPlayingSocketHub()
_api_manager = {"instance": APIStateManager(nowplaying_hub=_nowplaying_hub)}


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
    station_id: int = FastAPIPath(..., ge=0),
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
async def delete_radiostation(station_id: int = FastAPIPath(..., ge=0)):
    """Delete a radio station entry"""
    return _get_api_manager().delete_radiostation(station_id)


@app.post("/radiostations/{station_id}/play", response_model=RadioStationResponse)
async def play_radiostation(station_id: int = FastAPIPath(..., ge=0)):
    """Start playback for a radio station"""
    return _get_api_manager().play_radiostation(station_id)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws/nowplaying")
async def websocket_nowplaying(websocket: WebSocket):
    await _nowplaying_hub.connect(websocket)
    await websocket.send_json(_get_api_manager().get_state().model_dump())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _nowplaying_hub.disconnect(websocket)


def init_api_manager(eventbus, mopidy=None):
    _api_manager["instance"] = APIStateManager(eventbus, mopidy, _nowplaying_hub)


_webui_dir = Path(__file__).resolve().parent / "webui"
app.mount("/", StaticFiles(directory=str(_webui_dir), html=True), name="webui")
