"""Werkstattradio OLED controller"""
import asyncio
import signal
import importlib
from subprocess import call
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
from api.server import init_api_manager, start_api_server

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    eventbus = EventBus(loop)
    shutdown_started = False

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

    # Ensure GPIO devices always release cleanly on shutdown event.
    eventbus.subscribe(
        "system.shutdown_request",
        lambda _: RotaryEncoder.cleanup() if not settings.EMULATED else None
    )

    api_port = getattr(settings, 'API_PORT', 8000)
    api_path_prefix = getattr(settings, 'API_PATH_PREFIX', '/radio')
    api_server = start_api_server(loop, api_port, path_prefix=api_path_prefix)

    async def shutdown_runtime():
        nonlocal shutdown_started
        if shutdown_started:
            return

        shutdown_started = True

        print("Starting graceful shutdown")

        await api_server.shutdown(timeout=3)

        current_task = asyncio.current_task(loop=loop)
        pending = [
            task for task in asyncio.all_tasks(loop)
            if task is not current_task and not task.done()
        ]

        for task in pending:
            task.cancel()

        if pending:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*pending, return_exceptions=True),
                    timeout=3,
                )
            except asyncio.TimeoutError:
                print(f"Shutdown timeout: {len(pending)} task(s) still pending")

        loop.stop()

    def request_shutdown(execshutdown=False):
        if loop.is_closed():
            return
        payload = bool(execshutdown)
        if loop.is_running():
            eventbus.emit_threadsafe("system.shutdown_request", payload)
        else:
            system.execshutdown = system.execshutdown or payload
            loop.create_task(shutdown_runtime())

    # Handle system shutdown request
    def on_shutdown_request(payload):
        do_poweroff = bool(payload)
        if do_poweroff:
            system.execshutdown = True
        loop.create_task(shutdown_runtime())

    eventbus.subscribe("system.shutdown_request", on_shutdown_request)

    def _signal_handler(signum, _frame):
        print(f"Received signal {signum}, stopping service")
        request_shutdown(execshutdown=False)

    signal.signal(signal.SIGINT, _signal_handler)

    if settings.EMULATED:
        #pylint: disable=import-outside-toplevel
        from integrations.emulator import emulator
        emulator.start_emulator(loop)

    try:
        loop.run_forever()
    finally:
        loop.close()

    if system.execshutdown:
        print("Shutting down system")
        call(settings.SHUTDOWN_COMMAND, shell=True)


if __name__ == '__main__':
    main()
