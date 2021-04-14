"""Start file for Werkstattradio Oled controller"""
import importlib
import asyncio
import os
import settings
from hardware.display import get_display
from hardware.rotaryencoder import RotaryEncoder
from ui.windowmanager import WindowManager

def main():
    loop = asyncio.get_event_loop()

    #Display = real hardware or emulator (depending on settings)
    display = get_display(settings.EMULATED)

    #screen = windowmanager
    windowmanager = WindowManager(loop, display)

    #Import all window classes and generate objects of them
    for file in os.listdir("windows"):
        if file.endswith(".py") and file[0] != "_":
            name = file[:-3]
            module = importlib.import_module(f"windows.{name}")
            winclass = getattr(module, name.capitalize())
            window = winclass(windowmanager)
            windowmanager.add_window(name, window)

    #Load start window
    windowmanager.set_window("test")


    #Rotary encoder setup
    def turn_callback(direction):
        windowmanager.turn_callback(direction)

    def push_callback():
        windowmanager.push_callback()

    rotaryenc = RotaryEncoder(loop, settings.EMULATED, turn_callback, push_callback)



    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    finally:
        rotaryenc.cleanup()


if __name__ == '__main__':
    main()
