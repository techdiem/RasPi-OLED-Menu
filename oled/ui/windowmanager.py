"""Manages the currently shown activewindow on screen and passes callbacks for the rotary encoder"""
import asyncio

class WindowManager():
    def __init__(self, loop, device):
        self.device = device
        self.windows = {}
        self.activewindow = []
        self.loop = loop
        self.screenpower = True

        self.loop.create_task(self._render())
        print("Rendering task created")

    def add_window(self, windowid, window):
        self.windows[windowid] = window
        print(f"Added {windowid} window")

    def set_window(self, windowid):
        try:
            self.activewindow = self.windows[windowid]
            print(f"Activated {windowid}")
        except KeyError:
            print(f"Window {windowid} not found!")

    def clear_window(self):
        print("Show blank screen")
        self.screenpower = False
        self.device.clear()
        #Low-Power sleep mode
        self.device.hide()

    async def _render(self):
        while self.loop.is_running():
            if self.activewindow != [] and self.screenpower:
                try:
                    self.activewindow.render()
                except (NotImplementedError, AttributeError):
                    pass
            await asyncio.sleep(0.01)

    def push_callback(self):
        if self.screenpower:
            try:
                self.activewindow.push_callback()
            except (NotImplementedError, AttributeError):
                pass
        else:
            self.screenpower = True
            self.device.show()
            #TODO Set idle screen
            self.set_window("start")

    def turn_callback(self, direction):
        try:
            self.activewindow.turn_callback(direction)
        except (NotImplementedError, AttributeError):
            pass
