from PIL import ImageFont
import initGlobals
#for idle clock:
import math
import datetime
from time import sleep
from luma.core.render import canvas
today_last_time = "Unknown"

def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)

def menuentry(draw, x, y, text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
    draw.text((x+2, y+1), text, font=font, fill="white")

def drawmenu(draw, entries):
    position = 0
    for i in range(len(entries)):
        menuentry(draw, 6, 2+position*12, entries[i])
        position += 1

def drawIdle(device):
    global today_last_time
    now = datetime.datetime.now()
    today_date = now.strftime("%d %b %y")
    today_time = now.strftime("%H:%M")
    if today_time != today_last_time:
        today_last_time = today_time
        with canvas(device) as draw:
            now = datetime.datetime.now()
            today_date = now.strftime("%d %b %y")

            margin = 4

            cx = 30
            cy = min(device.height, 64) / 2

            left = cx - cy
            right = cx + cy

            hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
            hrs = posn(hrs_angle, cy - margin - 7)

            min_angle = 270 + (6 * now.minute)
            mins = posn(min_angle, cy - margin - 2)

            draw.ellipse((left + margin, margin, right - margin, min(device.height, 64) - margin), outline="white")
            draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
            draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
            draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill="white", outline="white")
            draw.text((2 * (cx + margin), cy - 8), today_date, fill="yellow")
            draw.text((2 * (cx + margin), cy), today_time, fill="yellow")
    sleep(0.1)


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
