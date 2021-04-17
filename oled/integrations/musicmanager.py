""" Manages music status and control commands for Mopidy and AirPlay """

class Musicmanager():
    def __init__(self, mopidyconnection, shairportconnection):
        self.mopidyconnection = mopidyconnection
        self.shairportconnection = shairportconnection
        self.playing = False
        self.source = "mpd"

    def airplay_callback(self, lis, info):
        if self.mopidyconnection.status()["state"] == "play" and self.source == "mpd":
            self.mopidyconnection.playpause()
            self.source = "airplay"

    def status(self):
        if self.source == "mpd":
            return self.mopidyconnection.status

    def nowplaying(self):
        if self.source == "mpd":
            return self.mopidyconnection.nowplaying
        elif self.source == "airplay":
            return self.shairportconnection.nowplaying()

    def playpause(self):
        if self.source == "mpd":
            return self.mopidyconnection.playpause()

    def previous(self):
        if self.source == "mpd":
            return self.mopidyconnection.previous()

    def next(self):
        if self.source == "mpd":
            return self.mopidyconnection.next()
