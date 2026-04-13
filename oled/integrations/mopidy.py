""" MPD integration """
import asyncio
from pathlib import Path
import time
import concurrent.futures
import threading
import musicpd
import settings # pylint: disable=import-error

class MopidyControl():
    def __init__(self, loop, eventbus=None):
        self.client = musicpd.MPDClient()
        self.loop = loop
        self.eventbus = eventbus
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._lock = threading.RLock()
        self._playlist_path = Path(settings.STATIONSPLAYLIST)
        self.connected = False
        self.radiostations = []
        self.nowplaying = {}
        self.status = ""
        self.load_radiostations()
        self._connectionlost()

    def connect(self):
        print("Connecting to Mopidy...")
        #try to disconnect, in case the connection is in an unknown state
        try:
            self.client.disconnect()
        except musicpd.ConnectionError:
            pass

        connectattempts = 0

        while not self.connected:
            try:
                self.client.connect(settings.MPD_IP, settings.MPD_PORT)
            except musicpd.ConnectionError:
                print("No connection possible, trying again...")
                connectattempts += 1
                if settings.EMULATED and connectattempts == 2:
                    print("EMULATED: Stopping mopidy connection attempts after 2 fails")
                    break
                time.sleep(10)
            else:
                print(f"Connected to MPD Version {self.client.mpd_version}")
                self.connected = True
                if self.eventbus is not None:
                    self.eventbus.emit_threadsafe("mopidy.connection", True)
                self.loop.create_task(self._update())

    def _connectionlost(self):
        self.connected = False
        if self.eventbus is not None:
            self.eventbus.emit_threadsafe("mopidy.connection", False)
        self.loop.run_in_executor(self.executor, self.connect)

    async def _update(self):
        while self.loop.is_running() and self.connected:
            try:
                new_nowplaying = self.client.currentsong()
                try:
                    new_status = self.client.status()['state']
                except KeyError:
                    new_status = self.status

                if new_nowplaying != self.nowplaying:
                    self.nowplaying = new_nowplaying
                    if self.eventbus is not None:
                        self.eventbus.emit("music.nowplaying", dict(self.nowplaying))

                if new_status != self.status:
                    self.status = new_status
                    if self.eventbus is not None:
                        self.eventbus.emit("music.playstate", self.status)
            except musicpd.ConnectionError:
                print("Error updating mopidy status, no connection!")
                self._connectionlost()

            await asyncio.sleep(10)

    def load_radiostations(self):
        """Load radio stations from the configured M3U file once."""
        try:
            stations = []
            with open(self._playlist_path, encoding="utf-8") as playlistfile:
                header = playlistfile.readline().strip()
                if header != '#EXTM3U':
                    print("Error loading radio stations: The m3u8 file is invalid!")
                else:
                    pending_title = None
                    for line in playlistfile:
                        line = line.strip()
                        if not line:
                            continue
                        # EXTINF line contains station name, following line contains URL.
                        # If EXTINF is missing, use URL as title.
                        if line.startswith('#EXTINF:'):
                            pending_title = line.split('#EXTINF:')[1].split(',',1)[1]
                            continue

                        title = pending_title if pending_title is not None else line
                        title = str(title).strip()
                        url = str(line).strip()
                        if title and url:
                            stations.append({"title": title, "url": url})
                        pending_title = None
        except FileNotFoundError:
            print("Error loading radio stations: File does not exist.")
            stations = []
        except PermissionError:
            print("Error loading radio stations: File cannot be accessed, check permissions.")
            stations = []

        with self._lock:
            self.radiostations.clear()
            self.radiostations.extend(stations)

    def get_radiostations(self):
        return self.radiostations

    def add_radiostation(self, title, url):
        with self._lock:
            title = str(title).strip()
            url = str(url).strip()
            if not title:
                raise ValueError("Radio station title must not be empty")
            if not url:
                raise ValueError("Radio station URL must not be empty")

            station = {"title": title, "url": url}
            self.radiostations.append(station)
            self._write_radiostations_to_file()
            return len(self.radiostations) - 1, dict(station)

    def update_radiostation(self, stationid, title=None, url=None):
        with self._lock:
            if stationid < 0 or stationid >= len(self.radiostations):
                raise IndexError("Radio station index out of range")

            station = self.radiostations[stationid]
            new_title = station["title"] if title is None else str(title).strip()
            new_url = station["url"] if url is None else str(url).strip()

            if not new_title:
                raise ValueError("Radio station title must not be empty")
            if not new_url:
                raise ValueError("Radio station URL must not be empty")

            station["title"] = new_title
            station["url"] = new_url
            self._write_radiostations_to_file()
            return dict(station)

    def delete_radiostation(self, stationid):
        with self._lock:
            if stationid < 0 or stationid >= len(self.radiostations):
                raise IndexError("Radio station index out of range")

            removed_station = self.radiostations.pop(stationid)
            self._write_radiostations_to_file()
            return dict(removed_station)

    def _write_radiostations_to_file(self):
        lines = ['#EXTM3U\n']
        for station in self.radiostations:
            lines.append(f"#EXTINF:-1,{station['title']}\n")
            lines.append(f"{station['url']}\n")

        self._playlist_path.write_text(''.join(lines), encoding="utf-8")

    def playpause(self):
        try:
            if self.status == "play":
                self.client.pause()
            else:
                self.client.play()
        except musicpd.ConnectionError:
            self._connectionlost()

    def next(self):
        try:
            self.client.next()
        except musicpd.ConnectionError:
            self._connectionlost()

    def previous(self):
        try:
            self.client.previous()
        except musicpd.ConnectionError:
            self._connectionlost()

    def stop(self):
        try:
            self.client.stop()
        except musicpd.ConnectionError:
            self._connectionlost()

    def playradiostation(self, stationid):
        #Start stream in background
        self.loop.run_in_executor(self.executor, self._playradiostation, stationid)

    def _playradiostation(self, stationid):
        try:
            with self._lock:
                if stationid < 0 or stationid >= len(self.radiostations):
                    print(f"Invalid radio station ID {stationid}")
                    return
                station = self.radiostations[stationid]

            self.client.clear()
            self.client.load(self._playlist_path.stem)
        except musicpd.ConnectionError:
            self._connectionlost()
            return
        try:
            self.client.play(stationid)
            print(f"Playing ID {stationid} ({station['title']})")
        except musicpd.ConnectionError:
            self._connectionlost()
            return
