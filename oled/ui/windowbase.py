""" View class to inherit other views from """

class WindowBase():
    def __init__(self, windowmanager, musicmanager):
        self.windowmanager = windowmanager
        self.musicmanager = musicmanager
        self.device = self.windowmanager.device
        self.loop = self.windowmanager.loop
        self.mopidyconnection = self.musicmanager.mopidyconnection

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()

    def push_callback(self):
        raise NotImplementedError()

    def turn_callback(self, direction):
        raise NotImplementedError()
