import asyncio
from fastapi import WebSocket
from .model import NowPlayingResponse

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
