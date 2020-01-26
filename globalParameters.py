import configparser

#Software-wide public variables
counter = 0
trigger = False
oldcounter = -1
activemenu = 0 #defaults to IDLE screen
oldactivemenu = -1 #needes for update thread
loadedPlaylist = "[Radio Streams]" #currently loaded Playlist; Radio Streams is loaded during startup
today_last_time = "Unknown"
clock_last_time = "Unknown"
########

#Load Config
print("Load configuration file")
config = configparser.ConfigParser()
config.read("settings.ini")

#Set fonts
print("Loading font configuration")
font_icons = config.get('Fonts', 'icons')
font_text = config.get('Fonts', 'text')
font_clock = config.get('Fonts', 'clock')
