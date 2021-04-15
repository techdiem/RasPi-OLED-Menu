""" Shairport-Sync metadata reader """
from shairportmetadatareader import AirplayPipeListener

class ShairportMetadata():
    def __init__(self, on_track_callback):
        self.airplaylistener = AirplayPipeListener()
        self.airplaylistener.bind(track_info=self._on_track_info)
        try:
            self.airplaylistener.start_listening()
        except FileNotFoundError:
            print("Shairport-Socket cannot be found, no AirPlay info avaiable!")
        self.on_track_callback = on_track_callback

    def _on_track_info(self, lis, info):
        del lis
        self.on_track_callback(info, self._nowplaying(info))

    @staticmethod
    def _nowplaying(info):
        if 'songartist' in info and 'itemname' in info:
            return f"{info['songartist']} - {info['itemname']}"
        elif 'itemname' in info:
            return info['itemname']
        else:
            return "AirPlay Streaming"

    def cleanup(self):
        self.airplaylistener.stop_listening()
