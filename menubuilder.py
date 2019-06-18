from PIL import ImageFont
import initGlobals

def menuentry(draw, x, y, text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
    draw.text((x+2, y+1), text, font=font, fill="white")

def drawmenu(draw, entries):
    position = 0
    for i in range(len(entries)):
        menuentry(draw, 6, 2+position*12, entries[i])
        position += 1

def menuUsed(draw, entries):
    counter = initGlobals.counter
    drawmenu(draw, entries)
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")

def buildMenu(menuid):
    initGlobals.activemenu = menuid
    initGlobals.counter = 0
    initGlobals.oldcounter = -1

def buildIdle():
    buildMenu(0)
    menu = ["Test", "Test2"]
    return menu

def buildMainMenu():
    buildMenu(1)
    menu = ["Zurück", "Wiedergabe stoppen", "Radio", "gespeicherte Musik", "Ausschalten"]
    return menu

def buildRadioMenu():
    buildMenu(2)
    menu = ["Zurück", "Sender2", "Sender3", "Sender4", "Sender5"]
    return menu

def buildShutdownMenu():
    buildMenu(3)
    menu = ["Wirklich herunterfahren?", "Nein", "Ja"]
    return menu

def buildSavedMenu():
    buildMenu(4)
    menu = ["Zurück", "Musik starten", "Nächster Titel", "Vorheriger Titel"]
    return menu
