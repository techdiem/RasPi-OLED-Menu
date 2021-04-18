"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
from subprocess import call
import settings
from integrations.display import get_display
from integrations.rotaryencoder import RotaryEncoder
from integrations.mopidy import MopidyControl
from integrations.shairport import ShairportMetadata
from integrations.musicmanager import Musicmanager
from ui.windowmanager import WindowManager
import windows.idle
import windows.mainmenu
import windows.playlistmenu
import windows.radiomenu
import windows.shutdownmenu
import windows.start

#Systemd exit
def gracefulexit(signaltype, frame):
    raise SystemExit
signal.signal(signal.SIGTERM, gracefulexit)

def main():
    loop = asyncio.get_event_loop()

    #Display = real hardware or emulator (depending on settings)
    display = get_display(settings.EMULATED)

    #screen = windowmanager
    windowmanager = WindowManager(loop, display)

    #Software integrations
    mopidy = MopidyControl(loop)
    def airplay_callback(info, nowplaying):
        musicmanager.airplay_callback(info, nowplaying)
    shairport = ShairportMetadata(airplay_callback)
    musicmanager = Musicmanager(mopidy, shairport)

    #Import all window classes and generate objects of them
    loadedwins = []
    idlescreen = windows.idle.Idle(windowmanager, musicmanager)
    shutdownscreen = windows.shutdownmenu.Shutdownmenu(windowmanager, mopidy)
    loadedwins.append(idlescreen)
    loadedwins.append(windows.mainmenu.Mainmenu(windowmanager))
    loadedwins.append(windows.playlistmenu.Playlistmenu(windowmanager, mopidy))
    loadedwins.append(windows.radiomenu.Radiomenu(windowmanager, mopidy))
    loadedwins.append(shutdownscreen)
    loadedwins.append(windows.start.Start(windowmanager, mopidy))

    for window in loadedwins:
        windowmanager.add_window(window.__class__.__name__.lower(), window)

    #Load start window
    windowmanager.set_window("start")


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
        loop.close()
        if shutdownscreen.execshutdown:
            call("sudo shutdown -h now", shell=True)


if __name__ == '__main__':
    main()
