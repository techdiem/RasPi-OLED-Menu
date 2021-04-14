"""
Manages the currently shown window on screen and passes the callbacks for the rotary encoder
"""

class Screen():
    def __init__(self, device):
        self.device = device
        self.window = []

    def set_window(self, window):
        self.window = window

    def render(self):
        try:
            self.window.render()
        except (NotImplementedError, AttributeError):
            pass

    def push_callback(self):
        try:
            self.window.push_callback()
        except (NotImplementedError, AttributeError):
            pass

    def turn_callback(self, direction):
        try:
            self.window.turn_callback(direction)
        except (NotImplementedError, AttributeError):
            pass
