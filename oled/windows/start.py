""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Start(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=35)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager, musicmanager)
        self._active = False
        self._waittimer = 0.0

    def activate(self):
        self._active = True
        self.mark_dirty()

    def deactivate(self):
        self._active = False

    def update(self, dt):
        if not self._active:
            return

        self._waittimer += dt
        if self._waittimer >= 1.0:
            self._waittimer = 0.0
            self.mark_dirty()

        if self.mopidyconnection.connected or settings.EMULATED:
            self.windowmanager.set_window("idle")

    def render(self):
        with canvas(self.device) as draw:
            draw.text((25, 3), text="Wird gestartet...", font=Start.font, fill="white")
            draw.text((50, 25), text="\uf251", font=Start.fontawesome, fill="white")

    def push_callback(self):
        pass

    def turn_callback(self, direction):
        pass
