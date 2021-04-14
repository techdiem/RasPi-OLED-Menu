""" Shairport-Sync metadata reader """
from shairportmetadatareader import AirplayPipeListener

class ShairportMetadata():
    def __init__(self):
        self.airplaylistener = AirplayPipeListener()
        self.airplaylistener.bind(track_info=self._on_track_info)
        self.airplaylistener.start_listening()
        self._info = ""

    def _on_track_info(self, lis, info):
        del lis
        self._info = info

    def nowplaying(self):
        if 'songartist' in self._info and 'itemname' in self._info:
            return f"{self._info['songartist']} - {self._info['itemname']}"
        elif 'itemname' in self._info:
            return self._info['itemname']
        else:
            return "AirPlay Streaming"

    def cleanup(self):
        self.airplaylistener.stop_listening()
