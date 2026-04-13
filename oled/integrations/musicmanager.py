""" Manages music status and control commands for Mopidy and AirPlay """

class Musicmanager():
    def __init__(self, mopidyconnection, shairportconnection, eventbus=None):
        self.mopidyconnection = mopidyconnection
        self.shairportconnection = shairportconnection
        self.eventbus = eventbus
        self.playing = False
        self.source = "mpd"
        self.volume = 100

        # Subscribe to volume changes
        if self.eventbus is not None:
            self.eventbus.subscribe("audio.volume", self._on_volume)
            self.eventbus.subscribe("airplay.connection", self._on_airplay_connection)

    def _on_volume(self, volume):
        """Update internal volume state from EventBus"""
        if volume is not None:
            self.volume = volume

    def _on_airplay_connection(self, connected):
        if connected is None:
            return

        if connected:
            if self.source == "mpd":
                self._set_source("airplay")
                print("Switched to AirPlay")
                if self.mopidyconnection.status == "play":
                    self.mopidyconnection.playpause()
            return

        if self.source == "airplay":
            print("Switched to MPD")
            self._set_source("mpd")

    def _set_source(self, source):
        if self.source != source:
            self.source = source
            if self.eventbus is not None:
                self.eventbus.emit("music.source", source)

    def status(self):
        if self.source == "mpd":
            return self.mopidyconnection.status

    def nowplaying(self):
        if self.source == "mpd":
            return self.mopidyconnection.nowplaying
        elif self.source == "airplay":
            if not self.shairportconnection.connected:
                print("Switched to MPD")
                self._set_source("mpd")
            return self.shairportconnection.nowplaying()

    def playpause(self):
        if self.source == "mpd":
            return self.mopidyconnection.playpause()

    def previous(self):
        if self.source == "mpd":
            return self.mopidyconnection.previous()
        elif self.source == "airplay":
            return self.shairportconnection.previous()

    def next(self):
        if self.source == "mpd":
            return self.mopidyconnection.next()
        elif self.source == "airplay":
            return self.shairportconnection.next()
