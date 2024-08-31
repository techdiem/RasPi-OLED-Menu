""" Shairport-Sync metadata reader """
import asyncio
from shairportmetadatareader import AirplayPipeListener, AirplayCommand

class ShairportMetadata():
    def __init__(self, loop, on_track_callback=None, volume_callback=None):
        self.loop = loop
        self.airplaylistener = AirplayPipeListener()
        self.airplaylistener.bind(track_info=self._on_track_info,
                                    connected=self._on_connect_info)
        try:
            self.airplaylistener.start_listening()
            print("Connected to Shairport Socket")
        except FileNotFoundError:
            print("Shairport Socket cannot be found, no AirPlay info avaiable!")
        self.on_track_callback = on_track_callback
        self.volume_callback = volume_callback
        self._info = {}
        self.connected = False
        self._airplayremote = None

    def _on_track_info(self, lis, info):
        self._info = info
        self.on_track_callback(lis, info)

    def _on_connect_info(self, lis, connected):
        del lis
        self.connected = connected
        if connected == True:
            self.loop.create_task(self._connectremote())
            self.loop.create_task(self.deviceVolumeObserver())

    async def _connectremote(self):
        while self.loop.is_running() and not self.airplaylistener.has_remote_data and self.connected:
            await asyncio.sleep(1)
        if self.airplaylistener.has_remote_data:
            self._airplayremote = self.airplaylistener.get_remote()
            print("AirPlay remote connected.")

    async def deviceVolumeObserver(self):
        old_vol = 0
        while self.loop.is_running() and self.connected:
            new_vol = round(self.airplaylistener.airplay_volume * 100)
            if (new_vol != old_vol):
                old_vol = new_vol
                print(f"Set volume to {new_vol}% from AirPlay")
                self.volume_callback(new_vol)
            await asyncio.sleep(0.5)

    def nowplaying(self):
        info = {}

        if 'songartist' in self._info and 'songalbum' in self._info:
            info['name'] = f"{self._info['songartist']}: {self._info['songalbum']}"
        elif 'songartist' in self._info:
            info['name'] = self._info['songartist']
        elif 'songalbum' in self._info:
            info['name'] = self._info['songalbum']
        else:
            info['name'] = self.airplaylistener.client_name

        if 'itemname' in self._info:
            info['title'] = self._info['itemname']
        else:
            info['title'] = "AirPlay Streaming"

        return info

    def next(self):
        self._airplayremote.send_command("nextitem")

    def previous(self):
        self._airplayremote.send_command("previtem")

    def cleanup(self):
        self.airplaylistener.stop_listening()
