"""Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import os
import importlib
import settings
from subprocess import call
from integrations.display import get_display
from integrations.rotaryencoder import RotaryEncoder
from integrations.volumepoti import VolumePoti
from integrations.alsa import AlsaMixer
from integrations.mopidy import MopidyControl
from integrations.shairport import ShairportMetadata
from integrations.musicmanager import Musicmanager
from integrations.system import system
from ui.windowmanager import WindowManager

#Systemd exit
def gracefulexit(signum, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, gracefulexit)

def main():
    loop = asyncio.new_event_loop()

    #Display = real hardware or emulator (depending on settings)
    display = get_display()

    #Software integrations
    mopidy = MopidyControl(loop)
    def airplay_callback(info, nowplaying):
        musicmanager.airplay_callback(info, nowplaying)
    def airplay_volume_changed(volume):
        amixer.set_volume(volume)
    shairport = ShairportMetadata(loop, airplay_callback, airplay_volume_changed)
    musicmanager = Musicmanager(mopidy, shairport)

    #Load windows
    windowmanager = WindowManager(loop, display)

    for name in os.listdir("windows"):
        if name.endswith(".py") and not name.startswith("__"):
            windowid = name[:-3]
            module = importlib.import_module(f"windows.{windowid}")
            windowclass = getattr(module, windowid.capitalize())
            window = windowclass(windowmanager, musicmanager)
            windowmanager.add_window(windowid, window)

    #Show start window
    windowmanager.set_window("start")

    #Set up rotary encoder
    RotaryEncoder(loop, windowmanager.turn_callback, windowmanager.push_callback)

    #Set up ADS1115 and potentiometer
    amixer = AlsaMixer(musicmanager)
    VolumePoti(loop, musicmanager, amixer)

    if settings.EMULATED:
        from integrations.emulator import emulator
        #emulator.start_emulator(loop)
    
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    finally:
        loop.close()

    if system.execshutdown:
        print("Shutting down system")
        call("sudo shutdown -h now", shell=True)


if __name__ == '__main__':
    main()
    RotaryEncoder.cleanup()
    sys.exit(0)
