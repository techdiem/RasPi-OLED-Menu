""" Shairport-Sync metadata reader """
from shairportmetadatareader import AirplayPipeListener

class ShairportMetadata():
    def __init__(self, on_track_callback=None):
        self.airplaylistener = AirplayPipeListener()
        self.airplaylistener.bind(track_info=self._on_track_info,
                                    connected=self._on_connect_info)
        try:
            self.airplaylistener.start_listening()
            print("Connected to Shairport Socket")
        except FileNotFoundError:
            print("Shairport Socket cannot be found, no AirPlay info avaiable!")
        self.on_track_callback = on_track_callback
        self._info = {}
        self.connected = False

    def _on_track_info(self, lis, info):
        self._info = info
        self.on_track_callback(lis, info)

    def _on_connect_info(self, lis, connected):
        del lis
        self.connected = connected

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

    def cleanup(self):
        self.airplaylistener.stop_listening()
