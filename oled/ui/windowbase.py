""" View class to inherit other views from """

class WindowBase():
    def __init__(self, windowmanager, musicmanager):
        self.windowmanager = windowmanager
        self.musicmanager = musicmanager
        self.eventbus = self.windowmanager.eventbus
        self.device = self.windowmanager.device
        self.loop = self.windowmanager.loop
        self.mopidyconnection = self.musicmanager.mopidyconnection
        self._dirty = True

    def mark_dirty(self):
        self._dirty = True

    def consume_dirty(self):
        if self._dirty:
            self._dirty = False
            return True
        return False

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()

    def update(self, dt):
        del dt

    def push_callback(self):
        raise NotImplementedError()

    def turn_callback(self, direction):
        raise NotImplementedError()
