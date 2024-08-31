import pygame
import asyncio

class EmulatedHWInput():
    def __init__(self):
        self.loop = None
        self.event_subscribers = []

    def start_emulator(self, loop):
        self.loop = loop
        self.loop.create_task(self._poll_key_events())

    async def _poll_key_events(self):
        while self.loop.is_running():
            event = pygame.event.poll()
            for sub in self.event_subscribers:
                await sub(event)
        await asyncio.sleep(0.01)

emulator = EmulatedHWInput()