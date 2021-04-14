""" View class to inherit other views from """
from luma.core.render import canvas

class WindowBase():
    def __init__(self, windowmanager):
        self.windowmanager = windowmanager
        self.canvas = canvas(self.windowmanager.device)
        self.loop = self.windowmanager.loop

    def render(self):
        raise NotImplementedError()

    def push_callback(self):
        raise NotImplementedError()

    def turn_callback(self, direction):
        raise NotImplementedError()