from PIL import ImageFont
from setupHandler import client, device
from subprocess import call

#Software-wide public variables
counter = 0
trigger = False
oldcounter = -1
activemenu = 0 #defaults to IDLE screen
########

def menuUsed(draw, entries):
    global counter
    position = 0
    #Draw menu
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

    #Draw entry selector
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")
        
def setScreen(screenid):
    global counter
    global activemenu
    global oldcounter
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
    setScreen(0)
    try:
        client.play(stationid)
    except:
        print("Error playing the station!")
    print("Playing station id", stationid)

def pausePlaying():
    setScreen(0)
    client.pause()