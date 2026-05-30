"""FastAPI server for REST endpoints"""
import asyncio
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Path as FastAPIPath, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .model import (NowPlayingResponse,
                    RadioStationResponse,
                    RadioStationCreateRequest,
                    RadioStationUpdateRequest)
from .apicontroller import APIController
from .nowplayingsocket import NowPlayingSocketHub


class APIServerRuntime:
    """Wraps the uvicorn server lifecycle for the OLED API."""

    def __init__(self, loop, port, path_prefix, host="0.0.0.0", log_level="info"):
        self.loop = loop
        self.port = port
        self.host = host
        self.log_level = log_level
        self.path_prefix = path_prefix
        self.server = None
        self.task = loop.create_task(self._run())

    async def _run(self):
        # Create wrapper with configured path prefix
        _wrapper = FastAPI()
        _wrapper.mount(self.path_prefix, app)

        @_wrapper.get("/", include_in_schema=False)
        async def root_redirect():
            return RedirectResponse(url=self.path_prefix + "/")

        config = uvicorn.Config(_wrapper, host=self.host, port=self.port, log_level=self.log_level)
        server = uvicorn.Server(config)
        self.server = server
        try:
            await server.serve()
        finally:
            self.server = None

    async def shutdown(self, timeout=3):
        if self.server is not None:
            self.server.should_exit = True

        if self.task.done():
            return

        try:
            await asyncio.wait_for(self.task, timeout=timeout)
        except asyncio.TimeoutError:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)


# ----------------------------
# FastAPI app and endpoint definitions

def start_api_server(loop, port, path_prefix, host="0.0.0.0", log_level="info"):
    return APIServerRuntime(loop, port, path_prefix, host=host, log_level=log_level)

def _get_api_manager():
    return _api_manager["instance"]

def init_api_manager(eventbus, mopidy=None):
    _api_manager["instance"] = APIController(eventbus, mopidy, _nowplaying_hub)

# Using a dict to allow late assignment from init_api_manager() without needing 'global' keyword
_nowplaying_hub = NowPlayingSocketHub()
_api_manager = {"instance": APIController(nowplaying_hub=_nowplaying_hub)}

app = FastAPI(title="RasPi OLED Menu API", version="1.0.0")

# ----------------------------
# Endpoint definitions

@app.get("/nowplaying", response_model=NowPlayingResponse)
async def get_nowplaying():
    return _get_api_manager().get_state()


@app.post("/nowplaying/stop", response_model=NowPlayingResponse)
async def stop_nowplaying():
    return _get_api_manager().stop_playback()


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


@app.websocket("/ws")
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

# Service static files for the web UI
_webui_dir = Path(__file__).resolve().parent / "webui"
app.mount("/", StaticFiles(directory=str(_webui_dir), html=True), name="webui")
