""" Mopidy/MPD integration """
import musicpd
import settings # pylint: disable=import-error

class MopidyControl():
    def __init__(self):
        self.client = musicpd.MPDClient()
        self._radiostations = []

    def connect(self):
        self.disconnect() #try to disconnect, in case the connection is in an unknown state
        try:
            self.client.connect(settings.MPD_IP, settings.MPD_PORT)
            print(f"Connected to MPD Version {self.client.mpd_version}")
        except ConnectionError:
            pass

    def status(self):
        return self.client.status()

    def nowplaying(self):
        return self.client.currentsong()

    def play(self):
        self.client.play()

    def pause(self):
        self.client.pause()

    def next(self):
        self.client.next()

    def previous(self):
        self.client.previous()

    def loadplaylist(self, name):
        self.client.clear()
        self.client.load(name)
        self.play()
        print(f"Loaded and playing Playlist {name}")

    def disconnect(self):
        try:
            self.client.disconnect()
        except ConnectionError:
            pass

    def _load_radiostations(self):
        try:
            playlistfile = open(settings.STATIONSPLAYLIST)
        except FileNotFoundError:
            print("Error loading radio stations: File does not exist.")

        #Check if it is a non-broken m3u8/m3u file
        line = playlistfile.readline()
        if not line.startswith('#EXTM3U'):
            print("Error loading radio stations: The m3u8 file is invalid!")

        for line in playlistfile:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # EXTINF line with information about the station
                title = line.split('#EXTINF:')[1].split(',',1)[1]
                self._radiostations.append(title)

        playlistfile.close()
