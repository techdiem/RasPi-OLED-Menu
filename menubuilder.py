from PIL import ImageFont
import initglobals

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
    counter = initglobals.counter
    drawmenu(draw, entries)
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")

def buildMenu(menuid):
    initglobals.activemenu = menuid
    initglobals.counter = 0
    initglobals.oldcounter = -1

def buildRadioMenu():
    buildMenu(2)
    menu = ["Sender1", "Sender2", "Sender3", "Sender4", "Sender5"]
    return menu

def buildMainMenu():
    buildMenu(1)
    menu = ["Wiedergabe stoppen", "Radio", "gespeicherte Musik", "Ausschalten"]
    return menu

def buildIdle():
    buildMenu(0)
    menu = ["zurück", "2"]
    return menu