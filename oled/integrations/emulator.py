import asyncio
import pygame

class EmulatedHWInput():
    def __init__(self):
        self.loop = None
        self.event_subscribers = []
        self._started = False

    def start_emulator(self, loop):
        if self._started:
            return

        pygame.init()
        self.loop = loop
        self.loop.create_task(self._poll_key_events())
        self._started = True

    async def _poll_key_events(self):
        while self.loop.is_running():
            event = pygame.event.poll()
            if event.type != pygame.NOEVENT:
                for sub in self.event_subscribers:
                    await sub(event)
            await asyncio.sleep(0.01)

emulator = EmulatedHWInput()
