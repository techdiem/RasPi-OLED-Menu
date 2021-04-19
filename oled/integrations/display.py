""" Display hardware or emulator """
import settings

def get_display():
    if settings.EMULATED:
        import luma.emulator.device

        class EmuPygame(luma.emulator.device.pygame):
            def display(self, image):
                super(EmuPygame, self).display(image)
                super(EmuPygame, self).display(image)

        print("Using PyGame output")
        #Mode=1: Monochrome
        return EmuPygame(transform='identity', scale=2, mode='1')

    else:
        from luma.oled.device import sh1106
        from luma.core.interface.serial import i2c

        device = sh1106(i2c(port=1, address=0x3C))
        device.contrast(245)
        print("Using real display hardware")
        return device
