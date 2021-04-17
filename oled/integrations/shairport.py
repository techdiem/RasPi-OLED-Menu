""" Shairport-Sync metadata reader """
from shairportmetadatareader import AirplayPipeListener

class ShairportMetadata():
    def __init__(self, on_track_callback):
        self.airplaylistener = AirplayPipeListener()
        self.airplaylistener.bind(track_info=self._on_track_info)
        try:
            self.airplaylistener.start_listening()
        except FileNotFoundError:
            print("Shairport Socket cannot be found, no AirPlay info avaiable!")
        self.on_track_callback = on_track_callback
        self._info = {}

    def _on_track_info(self, lis, info):
        del lis
        self._info = info
        self.on_track_callback(lis, info)

    def nowplaying(self):
        if 'songartist' in self._info and 'itemname' in self._info:
            info = {"name": self._info['songartist'], "title": self._info['itemname']}
        elif 'itemname' in self._info:
            info = {"name": self.airplaylistener.client_name, "title": self._info['itemname']}
        else:
            info = {"name": self.airplaylistener.client_name, "title": "AirPlay Streaming"}
        return info

    def cleanup(self):
        self.airplaylistener.stop_listening()
