"""Manages the currently shown activewindow on screen and passes callbacks for the rotary encoder"""
import asyncio
import time
try:
    from luma.core.sprite_system import framerate_regulator
except ImportError:
    framerate_regulator = None

class WindowManager():
    def __init__(self, loop, device, eventbus=None):
        self.device = device
        self.windows = {}
        self.activewindow = None
        self.loop = loop
        self.eventbus = eventbus
        self.screenpower = True
        self._fps = 15
        self._regulator = framerate_regulator(fps=self._fps)
        self.loop.create_task(self._render())
        print("Rendering task created")

    def add_window(self, windowid, window):
        self.windows[windowid] = window
        print(f"Added {windowid} window")

    def set_window(self, windowid):
        if windowid in self.windows:
            try:
                self.activewindow.deactivate()
            except (NotImplementedError, AttributeError):
                pass
            self.activewindow = self.windows[windowid]
            try:
                self.activewindow.activate()
            except (NotImplementedError, AttributeError):
                pass
            self.activewindow.mark_dirty()
            print(f"Activated {windowid}")
        else:
            print(f"Window {windowid} not found!")

    def clear_window(self):
        print("Show blank screen")
        self.screenpower = False
        self.device.clear()
        #Low-Power sleep mode
        self.device.hide()

    async def _render(self):
        last_tick = time.monotonic()
        while self.loop.is_running():
            now = time.monotonic()
            dt = now - last_tick
            last_tick = now

            if self.activewindow is not None and self.screenpower:
                try:
                    self.activewindow.update(dt)
                    #TODO: Das so lassen, oder besser nur framerate regulator statt sleep?
                    if self.activewindow.consume_dirty():
                        with self._regulator:
                            self.activewindow.render()
                    else:
                        await asyncio.sleep(1/self._fps)
                except (NotImplementedError, AttributeError):
                    pass
            else:
                await asyncio.sleep(1/self._fps)

    def push_callback(self):
        if self.screenpower:
            if self.activewindow is None:
                return
            try:
                self.activewindow.push_callback()
                self.activewindow.mark_dirty()
            except (NotImplementedError, AttributeError):
                pass
        else:
            self.screenpower = True
            self.device.show()
            self.set_window("idle")

    def turn_callback(self, direction):
        if self.activewindow is None:
            return
        try:
            self.activewindow.turn_callback(direction)
            self.activewindow.mark_dirty()
        except (NotImplementedError, AttributeError):
            pass
