""" MPD integration """
import asyncio
from pathlib import Path
import threading
import musicpd
import settings # pylint: disable=import-error

class MopidyControl():
    def __init__(self, loop, eventbus=None):
        self.client = musicpd.MPDClient()
        self.client.timeout = getattr(settings, "MPD_CONNECT_TIMEOUT", 2)
        self.loop = loop
        self.eventbus = eventbus
        self._lock = threading.RLock()
        self._playlist_path = Path(settings.STATIONSPLAYLIST)
        self.connected = False
        self.radiostations = []
        self.nowplaying = {}
        self.status = ""
        self._shutting_down = False
        self._connect_task = None
        self._update_task = None
        self._reconnect_interval = getattr(settings, "MPD_RECONNECT_INTERVAL", 10)

        if self.eventbus is not None:
            self.eventbus.subscribe("system.shutdown_request", self._on_shutdown_request)

        self.load_radiostations()
        self._schedule_connect()

    def _schedule_connect(self):
        if self._shutting_down:
            return

        if self._connect_task is None or self._connect_task.done():
            self._connect_task = self.loop.create_task(self._connect_loop())

    async def _run_client(self, method, *args, **kwargs):
        # Führt blocking MPD-Befehle im Thread-Pool aus (library ist synchron/blocking)
        return await asyncio.to_thread(self._run_client_blocking, method, *args, **kwargs)

    def _run_client_blocking(self, method, *args, **kwargs):
        # Thread-sicher durch Lock
        with self._lock:
            return method(*args, **kwargs)

    async def _connect_loop(self):
        print("Connecting to Mopidy...")
        connectattempts = 0

        while self.loop.is_running() and not self._shutting_down and not self.connected:
            try:
                try:
                    await self._run_client(self.client.disconnect)
                except musicpd.ConnectionError:
                    pass

                await self._run_client(self.client.connect, settings.MPD_IP, settings.MPD_PORT)
            except (musicpd.ConnectionError, OSError):
                print("No connection possible, trying again...")
                connectattempts += 1
                if settings.EMULATED and connectattempts == 2:
                    print("EMULATED: Stopping mopidy connection attempts after 2 fails")
                    return

                await asyncio.sleep(self._reconnect_interval)
                continue

            print(f"Connected to MPD Version {self.client.mpd_version}")
            self.connected = True
            if self.eventbus is not None:
                self.eventbus.emit_threadsafe("mopidy.connection", True)

            if self._update_task is None or self._update_task.done():
                self._update_task = self.loop.create_task(self._update())
            return

    def _connectionlost(self):
        if self._shutting_down:
            return

        was_connected = self.connected
        self.connected = False
        if was_connected and self.eventbus is not None:
            self.eventbus.emit_threadsafe("mopidy.connection", False)

        self._schedule_connect()

    async def _update(self):
        while self.loop.is_running() and self.connected and not self._shutting_down:
            try:
                new_nowplaying = await self._run_client(self.client.currentsong)
                try:
                    status_response = await self._run_client(self.client.status)
                    new_status = status_response.get("state", self.status)
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
            except (musicpd.ConnectionError, OSError):
                print("Error updating mopidy status, no connection!")
                self._connectionlost()
                return

            await asyncio.sleep(10)

    def _on_shutdown_request(self, _):
        self._shutting_down = True
        self.connected = False

        if self._connect_task is not None and not self._connect_task.done():
            self._connect_task.cancel()

        if self._update_task is not None and not self._update_task.done():
            self._update_task.cancel()

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

    async def _playpause(self):
        try:
            if self.status == "play":
                await self._run_client(self.client.pause)
            else:
                await self._run_client(self.client.play)
        except (musicpd.ConnectionError, OSError):
            self._connectionlost()

    def playpause(self):
        self.loop.create_task(self._playpause())

    async def _next(self):
        try:
            await self._run_client(self.client.next)
        except (musicpd.ConnectionError, OSError):
            self._connectionlost()

    def next(self):
        self.loop.create_task(self._next())

    async def _previous(self):
        try:
            await self._run_client(self.client.previous)
        except (musicpd.ConnectionError, OSError):
            self._connectionlost()

    def previous(self):
        self.loop.create_task(self._previous())

    async def _stop(self):
        try:
            await self._run_client(self.client.stop)
        except (musicpd.ConnectionError, OSError):
            self._connectionlost()

    def stop(self):
        self.loop.create_task(self._stop())

    async def _playradiostation(self, stationid):
        try:
            with self._lock:
                if stationid < 0 or stationid >= len(self.radiostations):
                    print(f"Invalid radio station ID {stationid}")
                    return
                station = self.radiostations[stationid]

            await self._run_client(self.client.clear)
            await self._run_client(self.client.load, self._playlist_path.stem)
            await self._run_client(self.client.play, stationid)
            print(f"Playing ID {stationid} ({station['title']})")
        except (musicpd.ConnectionError, OSError):
            self._connectionlost()

    def playradiostation(self, stationid):
        self.loop.create_task(self._playradiostation(stationid))
