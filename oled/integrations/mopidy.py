""" Mopidy/MPD integration """
import asyncio
import musicpd
import settings # pylint: disable=import-error

class MopidyControl():
    def __init__(self, loop):
        self.client = musicpd.MPDClient()
        self.loop = loop
        self.connected = False
        self._radiostations = []
        self._playlists = []
        self._nowplaying = {}
        self._status = {}
        self.loop.create_task(self.connect())

    async def connect(self):
        print("Connecting to Mopidy...")
        self.disconnect() #try to disconnect, in case the connection is in an unknown state
        while self.loop.is_running():
            if not self.connected:
                try:
                    self.client.connect(settings.MPD_IP, settings.MPD_PORT)
                    print(f"Connected to MPD Version {self.client.mpd_version}")
                    self.connected = True
                    self.loop.create_task(self._refresh_content())
                    self.loop.create_task(self._update())
                except musicpd.ConnectionError:
                    print("No connection possible, trying again...")
            await asyncio.sleep(10)

    def status(self):
        return self._status

    def nowplaying(self):
        return self._nowplaying

    async def _update(self):
        while self.loop.is_running() and self.connected:
            try:
                self._nowplaying = self.client.currentsong()
                self._status = self.client.status()
            except musicpd.ConnectionError:
                print("Error updating mopidy status, no connection!")
                self.connected == False

            await asyncio.sleep(10)

    async def _refresh_content(self):
        while self.loop.is_running() and self.connected:
            await self._refresh_radiostations()
            await self._refresh_playlists()
            await asyncio.sleep(300)


    async def _refresh_radiostations(self):
        #Load Radio stations
        try:
            playlistfile = open(settings.STATIONSPLAYLIST)
        except FileNotFoundError:
            print("Error loading radio stations: File does not exist.")
            return None

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

    async def _refresh_playlists(self):
        #Load playlists
        try:
            playlists = self.client.listplaylists()
        except musicpd.ConnectionError:
            print("Error loading playlists, no connection!")
            self.connected = False
        for playlist in playlists:
            if playlist["playlist"] != "[Radio Streams]":
                self._playlists.append(playlist["playlist"])


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
        except musicpd.ConnectionError:
            pass

