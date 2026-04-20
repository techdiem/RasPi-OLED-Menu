from typing import List
from fastapi import HTTPException
from .model import NowPlayingResponse, RadioStationResponse

class APIController:
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