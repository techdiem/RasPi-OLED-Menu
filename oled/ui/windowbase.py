""" View class to inherit other views from """

class WindowBase():
    def __init__(self, windowmanager):
        self.windowmanager = windowmanager
        self.device = self.windowmanager.device
        self.loop = self.windowmanager.loop

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
