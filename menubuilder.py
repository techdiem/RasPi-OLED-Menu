from PIL import ImageFont
import initGlobals
from luma.core.render import canvas

def drawmenu(draw, entries):
    position = 0
    for i in range(len(entries)):
        x = 6
        y = 2+position*12
        fontawesome = ImageFont.truetype("fonts/fontawesome.ttf", size=10)
        font = ImageFont.truetype("fonts/bahnschrift.ttf", size=10)
        draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
        if entries[i] == "Zurück":
            draw.text((x+2, y+1), text="\uf053", font=fontawesome, fill="white")
            draw.text((x+12, y), "Zurück", font=font, fill="white")
        else:
            draw.text((x+2, y), entries[i], font=font, fill="white")

        position += 1

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
