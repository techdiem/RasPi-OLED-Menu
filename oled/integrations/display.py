""" Display hardware or emulator """
import settings

class CachedDisplayProxy:
    """Proxy that forwards display updates only when frame content changes."""
    def __init__(self, device):
        self._device = device
        self._last_frame = None

    def display(self, image):
        frame = image.tobytes()
        if frame != self._last_frame:
            self._last_frame = frame
            self._device.display(image)

    def clear(self):
        self._last_frame = None
        self._device.clear()

    def hide(self):
        self._last_frame = None
        return self._device.hide()

    def show(self):
        self._last_frame = None
        return self._device.show()

    def __getattr__(self, name):
        return getattr(self._device, name)

def get_display():
    if settings.EMULATED:
        import luma.emulator.device

        class EmuPygame(luma.emulator.device.pygame):
            def display(self, image):
                super(EmuPygame, self).display(image)
                super(EmuPygame, self).display(image)

        print("Using PyGame output")
        #Mode=1: Monochrome
        return CachedDisplayProxy(EmuPygame(transform='identity', scale=2, mode='1'))

    else:
        from luma.oled.device import sh1106
        from luma.core.interface.serial import i2c

        device = sh1106(i2c(port=1, address=0x3C))
        device.contrast(245)
        print("Using real display hardware")
        return CachedDisplayProxy(device)
