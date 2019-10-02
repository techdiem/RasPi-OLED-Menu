from PIL import ImageFont
from setupHandler import client, device, font_icons, font_text, config
from subprocess import call
from time import sleep
import threading

#Software-wide public variables
counter = 0
trigger = False
oldcounter = -1
activemenu = 0 #defaults to IDLE screen
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
    activemenu = screenid
    counter = 0
    oldcounter = -1

def shutdownSystem():
    print("Shutting down system")
    try:
        client.stop()
    except: pass
    device.cleanup()
    call("sudo shutdown -h now", shell=True)
    exit()

def playRadioStation(stationid):
    print("Playing station id", stationid)
    setScreen(0)
    try:
        client.play(stationid)
    except:
        print("Error playing the station!")
        reconnect()

def pausePlaying():
    setScreen(0)
    try:
        client.pause()
    except:
        print("Error pausing the playback!")
        reconnect()

def mpd_reconnect():
    #Disconnect
    try:
        client.close()
    except: pass
    sleep(10)
    #Connect
    try:
        print("Reconnecting...")
        client.connect(config.get('MPD', 'ip'), int(config.get('MPD', 'port')))
        print("Successfully connected")
    except: 
        print("Reconnect failed, could not open the connection!")

def reconnect():
    #run reconnect in second thread
    t = threading.Thread(target=mpd_reconnect)
    t.start()

def drawStart():
    global font_text
    #NEW LOADINGSCREEN HERE

def bigError(message):
    global font_text, font_icons
    #ERROR PAGE HERE