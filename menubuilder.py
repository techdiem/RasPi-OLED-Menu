from PIL import ImageFont
import initGlobals
#for idle clock:
import math
import datetime
from time import sleep
from luma.core.render import canvas
from setupHandler import client
today_last_time = "Unknown"

def menuentry(draw, x, y, text):
    fontawesome = ImageFont.truetype("fonts/fontawesome.ttf", size=10)
    font = ImageFont.truetype("fonts/bahnschrift.ttf", size=10)
    draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
    if text == "Zurück":
        draw.text((x+2, y+1), text="\uf053", font=fontawesome, fill="white")
        draw.text((x+12, y), text, font=font, fill="white")
    else:
        draw.text((x+2, y), text, font=font, fill="white")

def drawmenu(draw, entries):
    position = 0
    for i in range(len(entries)):
        menuentry(draw, 6, 2+position*12, entries[i])
        position += 1

def drawIdle(device):
    global today_last_time
    clockfont = ImageFont.truetype("fonts/kristenITC.ttf", size=35)
    font = ImageFont.truetype("fonts/calibri.ttf", size=12)
    fontawesome = ImageFont.truetype("fonts/fontawesome.ttf", size=12)
    now = datetime.datetime.now()
    today_time = now.strftime("%H:%M")
    if today_time != today_last_time:
        today_last_time = today_time
        with canvas(device) as draw:
            now = datetime.datetime.now()

            draw.text((20, 3), today_time, font=clockfont, fill="white")
            try:
                playingInfo = client.currentsong()
            except:
                playingInfo = {'title': 'Could not load name!'}
            if playingInfo != {}:
                currentSong = playingInfo["title"]
                draw.text((12, 48), currentSong[0:21], font=font, fill="white")
                draw.text((0, 45), text="\uf001", font=fontawesome, fill="white")

def menuUsed(draw, entries):
    counter = initGlobals.counter
    drawmenu(draw, entries)
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")
        
def buildMenu(menuid):
    initGlobals.activemenu = menuid
    initGlobals.counter = 0
    initGlobals.oldcounter = -1

def buildMainMenu():
    buildMenu(1)
    menu = ["Zurück", "Wiedergabe stoppen", "Radio", "gespeicherte Musik", "Ausschalten"]
    return menu

def buildRadioMenu():
    buildMenu(2)
    try:
        savedStations = client.listplaylistinfo("[Radio Streams]")
        menu = ["Zurück", ]
        for station in savedStations:
            menu.append(station["title"])
    except:
        menu = buildMainMenu()
        
    return menu

def buildShutdownMenu():
    buildMenu(3)
    menu = ["Wirklich herunterfahren?", "Nein", "Ja"]
    return menu

def buildSavedMenu():
    buildMenu(4)
    menu = ["Zurück", "Musik starten", "Nächster Titel", "Vorheriger Titel"]
    return menu
