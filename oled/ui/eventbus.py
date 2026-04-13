"""Simple in-process event bus for decoupled component communication.

Event Bus Topics:
  Input:
    input.turn (direction: int) - Rotary encoder turn event
    input.push (None) - Rotary encoder push event
  
  Audio:
    audio.volume (volume: int) - Volume changed (0-100%)
  
  Music:
    music.nowplaying (info: dict) - Currently playing track
    music.playstate (state: str) - Playback state (play/pause/stop)
    music.source (source: str) - Active source (mpd/airplay)
  
  Connections:
    mopidy.connection (connected: bool) - MPD connection status
    airplay.connection (connected: bool) - AirPlay connection status
  
  System:
    system.shutdown_request (None) - Graceful shutdown signal
"""
import inspect
from collections import defaultdict

class EventBus:
    def __init__(self, loop):
        self.loop = loop
        self._subscribers = defaultdict(list)

    def subscribe(self, event_name, callback):
        self._subscribers[event_name].append(callback)

    def emit(self, event_name, payload=None):
        callbacks = list(self._subscribers.get(event_name, []))
        for callback in callbacks:
            self.loop.call_soon(callback, payload)

    def emit_threadsafe(self, event_name, payload=None):
        callbacks = list(self._subscribers.get(event_name, []))
        for callback in callbacks:
            self.loop.call_soon_threadsafe(callback, payload)

    async def emit_async(self, event_name, payload=None):
        callbacks = list(self._subscribers.get(event_name, []))
        for callback in callbacks:
            if inspect.iscoroutinefunction(callback):
                await callback(payload)
            else:
                callback(payload)
