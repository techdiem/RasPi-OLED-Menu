""" Radio menu """
from ui.menubase import MenuBase

class Radiomenu(MenuBase):
    def __init__(self, windowmanager, mopidyconnection):
        self.mopidyconnection = mopidyconnection
        super().__init__(windowmanager, "Radiosender")

    def activate(self):
        self.menu = self.mopidyconnection.radiostations

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            self.mopidyconnection.playradiostation(self.counter + self.page - 1)
            self.windowmanager.set_window("idle")
