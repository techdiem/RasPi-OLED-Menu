""" Playlist menu """
from ui.menubase import MenuBase

class Playlistmenu(MenuBase):
    def __init__(self, windowmanager, mopidyconnection):
        self.mopidyconnection = mopidyconnection
        super().__init__(windowmanager, "Playlists", self.mopidyconnection.playlists)

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            #TODO load playlist
            self.windowmanager.set_window("idle")
