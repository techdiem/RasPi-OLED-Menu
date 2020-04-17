import configparser

class globalParameterHandler():
    def __init__(self):
        #Software-wide public variables
        self.counter = 0
        self.trigger = False
        self.oldcounter = -1
        self.activemenu = 0 #defaults to IDLE screen
        self.oldactivemenu = -1 #needes for update thread
        self.loadedPlaylist = "[Radio Streams]" #currently loaded Playlist; Radio Streams is loaded during startup
        self.today_last_time = "Unknown"
        self.clock_last_time = "Unknown"
        ########

        #Load Config
        print("Load configuration file")
        self.config = configparser.ConfigParser()
        self.config.read("settings.ini")

        #Set fonts
        print("Loading font configuration")
        self.font_icons = self.config.get('Fonts', 'icons')
        self.font_text = self.config.get('Fonts', 'text')
        self.font_clock = self.config.get('Fonts', 'clock')

    def setScreen(self, screenid):
        self.activemenu = screenid
        self.counter = 0
        self.oldcounter = -1
        self.today_last_time = "Unknown"
        self.clock_last_time = "Unknown"

globalParameters = globalParameterHandler()