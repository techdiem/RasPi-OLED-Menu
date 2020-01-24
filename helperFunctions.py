from PIL import ImageFont
from setupHandler import device, font_icons, font_text, config, client, establishConnection
from subprocess import call
from time import sleep
import threading
from luma.core.render import canvas

#Software-wide public variables
counter = 0
trigger = False
oldcounter = -1
activemenu = 0 #defaults to IDLE screen
loadedPlaylist = "[Radio Streams]" #currently loaded Playlist; Radio Streams is loaded during startup
today_last_time = "Unknown"
clock_last_time = "Unknown"
########

def drawMenu(draw, entries):
    global counter
    global font_text, font_icons
    position = 0
    #Draw menu
    for i in range(len(entries)):
        x = 6
        y = 2+position*12
        fontawesome = ImageFont.truetype(font_icons, size=10)
        font = ImageFont.truetype(font_text, size=10)
        draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
        if entries[i] == "Zurück":
            draw.text((x+2, y+2), text="\uf053", font=fontawesome, fill="white")
            draw.text((x+12, y+1), "Zurück", font=font, fill="white")
        else:
            draw.text((x+2, y+1), entries[i], font=font, fill="white")
        position += 1

    #Draw entry selector
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")
        
def setScreen(screenid):
    global counter, oldcounter, activemenu
    global today_last_time, clock_last_time
    activemenu = screenid
    counter = 0
    oldcounter = -1
    today_last_time = "Unknown"
    clock_last_time = "Unknown"

def shutdownSystem():
    print("Shutting down system")
    try:
        client.stop()
    except: pass
    device.cleanup()
    call("sudo shutdown -h now", shell=True)
    exit()

def playRadioStation(stationid):
    print("Playing ID", stationid)
    try:
        client.play(stationid)
    except:
        print("Error playing the station!")
        establishConnection()
    setScreen(0)

def playbackControl(command):
    try:
        if command == "pause": client.pause()
        elif command == "previous": client.previous()
        elif command == "next": client.next()
        elif command == "play": client.play()
        print("Playback:", command)
    except:
        print("Error changing the playback mode!")
        establishConnection()
    setScreen(0)

def loadPlaylists():
    global playlists
    try:
        playlists = []
        clientplaylists = client.listplaylists()
        for playlist in clientplaylists:
            if playlist["playlist"] != "[Radio Streams]":
                playlists.append(playlist["playlist"])
    except:
        print("Error loading list of playlists!")
        establishConnection()

def loadPlaylist(name):
    global loadedPlaylist
    try:
        client.clear()
        client.load(name)
        client.shuffle()
        loadedPlaylist = name
        print("Loaded and playing Playlist", name)
        client.play()
    except:
        print("Error loading and playing Playlist", name)
        establishConnection()
