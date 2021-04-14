"""Start file for Werkstattradio Oled controller"""
import asyncio
import settings
from hardware.display import get_display
from hardware.rotaryencoder import RotaryEncoder
from ui.screen import Screen
from windows.test import TestView

def main():
    loop = asyncio.get_event_loop()

    display = get_display(settings.EMULATED)

    screen = Screen(loop, display)

    testview = TestView(display)
    screen.add_window("test", testview)
    screen.set_window("test")

    def turn_callback(direction):
        screen.turn_callback(direction)

    rotaryenc = RotaryEncoder(loop, settings.EMULATED, turn_callback)

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    finally:
        rotaryenc.cleanup()


if __name__ == '__main__':
    main()
