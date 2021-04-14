"""
Display hardware or emulator
"""

def display(emulated):
    if emulated:
        import luma.emulator.device

        class EmuPygame(luma.emulator.device.pygame):
            def display(self, image):
                super(EmuPygame, self).display(image)
                super(EmuPygame, self).display(image)

        return EmuPygame(transform='identity', scale=4, mode='1')

    else:
        from luma.oled.device import sh1106
        from luma.core.interface.serial import i2c

        device = sh1106(i2c(port=1, address=0x3C))
        device.contrast(245)
        return device
