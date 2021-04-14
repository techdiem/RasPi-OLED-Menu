""" View class to inherit other views from """
from luma.core.render import canvas

class Window():
    def __init__(self, device):
        self.canvas = canvas(device)

    def render(self):
        raise NotImplementedError()

    def push_callback(self):
        raise NotImplementedError()

    def turn_callback(self, direction):
        raise NotImplementedError()
