"""Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import importlib
from subprocess import call
import uvicorn
import settings
from integrations.display import get_display
from integrations.rotaryencoder import RotaryEncoder
from integrations.volumepoti import VolumePoti
from integrations.alsa import AlsaMixer
from integrations.mopidy import MopidyControl
from integrations.shairport import ShairportMetadata
from integrations.musicmanager import Musicmanager
from integrations.system import system
from integrations.mqtt import MqttConnection
from ui.windowmanager import WindowManager
from ui.eventbus import EventBus
from api.server import app as api_app, init_api_manager

#Systemd exit
def gracefulexit(_signum, _frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, gracefulexit)

async def run_api_server(port: int = 8000):
    """Run FastAPI server in asyncio event loop"""
    config = uvicorn.Config(api_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

def main():
    loop = asyncio.new_event_loop()
    eventbus = EventBus(loop)

    # Display = real hardware or emulator (depending on settings)
    display = get_display()

    # Initialize integrations with minimal coupling (only loop + eventbus)
    mopidy = MopidyControl(loop, eventbus)
    shairport = ShairportMetadata(loop, eventbus)
    musicmanager = Musicmanager(mopidy, shairport, eventbus)

    # Initialize API state manager to subscribe to EventBus and expose Mopidy data
    init_api_manager(eventbus, mopidy)

    # Initialize MQTT bridge to EventBus
    MqttConnection(eventbus)

    # Load windows
    windowmanager = WindowManager(loop, display, eventbus)
    eventbus.subscribe("input.turn", windowmanager.turn_callback)
    eventbus.subscribe("input.push", lambda _: windowmanager.push_callback())

    for windowid in ["start", "idle", "radiomenu", "shutdownmenu"]:
        module = importlib.import_module(f"windows.{windowid}")
        windowclass = getattr(module, windowid.capitalize())
        window = windowclass(windowmanager, musicmanager)
        windowmanager.add_window(windowid, window)

    windowmanager.set_window("start")

    # Set up input devices
    RotaryEncoder(loop,
                  lambda direction: eventbus.emit_threadsafe("input.turn", direction),
                  lambda: eventbus.emit_threadsafe("input.push"))

    # Set up audio control (subscribes to volume events internally)
    AlsaMixer(eventbus)
    VolumePoti(loop, eventbus)

    # Handle system shutdown request
    async def on_shutdown_request(_):
        mopidy.stop()
        system.execshutdown = True
        print("Stopping event loop")
        loop.stop()

    eventbus.subscribe("system.shutdown_request", on_shutdown_request)

    # Start FastAPI server in background
    api_port = getattr(settings, 'API_PORT', 8000)
    loop.create_task(run_api_server(api_port))

    if settings.EMULATED:
        #pylint: disable=import-outside-toplevel
        from integrations.emulator import emulator
        emulator.start_emulator(loop)

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
