from PIL import ImageFont
from setupHandler import device, client, establishConnection
from globalParameters import globalParameters, mediaVariables
from subprocess import call
from time import sleep
import threading
from luma.core.render import canvas

def drawMenu(draw, entries):
    counter = globalParameters.counter
    position = 0
    #Draw menu
    for i in range(len(entries)):
        x = 6
        y = 2+position*12
        fontawesome = ImageFont.truetype(globalParameters.font_icons, size=10)
        font = ImageFont.truetype(globalParameters.font_text, size=10)
        draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
        if entries[i] == "Zurück":
            draw.text((x+2, y+2), text="\uf053", font=fontawesome, fill="white")
            draw.text((x+12, y+1), "Zurück", font=font, fill="white")
        else:
            draw.text((x+2, y+1), entries[i], font=font, fill="white")
        position += 1

    #Draw entry selector
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")

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
    globalParameters.setScreen(0)

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
    globalParameters.setScreen(0)

def loadRadioStations():
    try:
        client.clear()
        client.load("[Radio Streams]")
        mediaVariables.loadedPlaylist = "[Radio Streams]"
    except:
        print("Error loading radio station playlist!")
        establishConnection()

def loadPlaylist(name):
    try:
        client.clear()
        client.load(name)
        client.shuffle()
        mediaVariables.loadedPlaylist = name
        print("Loaded and playing Playlist", name)
        client.play()
    except:
        print("Error loading and playing Playlist", name)
        establishConnection()
