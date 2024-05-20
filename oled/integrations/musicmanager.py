""" Manages music status and control commands for Mopidy and AirPlay """

class Musicmanager():
    def __init__(self, mopidyconnection, shairportconnection):
        self.mopidyconnection = mopidyconnection
        self.shairportconnection = shairportconnection
        self.playing = False
        self.source = "mpd"
        self.volume = 100

    def airplay_callback(self, lis, info):
        del lis, info
        if self.source == "mpd":
            self.source = "airplay"
            print("Switched to AirPlay")
            if self.mopidyconnection.status == "play":
                self.mopidyconnection.playpause()

    def status(self):
        if self.source == "mpd":
            return self.mopidyconnection.status

    def nowplaying(self):
        if self.source == "mpd":
            return self.mopidyconnection.nowplaying
        elif self.source == "airplay":
            if not self.shairportconnection.connected:
                print("Switched to MPD")
                self.source = "mpd"
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
