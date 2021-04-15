""" Radio menu """
from ui.menubase import MenuBase

class Radiomenu(MenuBase):
    def __init__(self, windowmanager):
        #TODO get stations
        self.menu = ["abcd", "kjksbdf", "lkasd"]
        super().__init__(windowmanager, "Radiosender", self.menu)

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            #TODO load radio station
            self.windowmanager.set_window("idle")
