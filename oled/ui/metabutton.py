class MetaButton():
    """Represents an interactable button"""
    def __init__(self, posx, posy, icon, action):
        self.posx = posx
        self.posy = posy
        self.icon = icon
        self.action = action

    def trigger(self):
        return self.action()
