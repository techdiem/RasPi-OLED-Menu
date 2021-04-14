""" Manages the currently shown activewindow on screen and passes the callbacks for the rotary encoder """
import asyncio

class Screen():
    def __init__(self, loop, device):
        self.device = device
        self.windows = {}
        self.activewindow = []
        self.loop = loop

        self.loop.create_task(self._render())
        print("Rendering task created")

    def add_window(self, windowid, window):
        self.windows[windowid] = window
        print("Window added", windowid)

    def set_window(self, windowid):
        self.activewindow = self.windows[windowid]
        print(windowid, "activated")

    async def _render(self):
        while self.loop.is_running():
            if self.activewindow != []:
                try:
                    self.activewindow.render()
                except (NotImplementedError, AttributeError):
                    pass
                await asyncio.sleep(0.01)

    def push_callback(self):
        try:
            self.activewindow.push_callback()
        except (NotImplementedError, AttributeError):
            pass

    def turn_callback(self, direction):
        try:
            self.activewindow.turn_callback(direction)
        except (NotImplementedError, AttributeError):
            pass
