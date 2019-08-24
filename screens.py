from PIL import ImageFont
##Imports for clock##
import math
import datetime
####
from luma.core.render import canvas
import initGlobals
from helperFunctions import *

today_last_time = "Unknown"
page = 0

#IDLE screen with clock and current playing song (screenid: 0)
class idlescreen():
    #Used in main Loop to create the screen
    @staticmethod
    def draw(device):
        global today_last_time
        clockfont = ImageFont.truetype("fonts/kristenITC.ttf", size=35)
        font = ImageFont.truetype("fonts/calibri.ttf", size=12)
        fontawesome = ImageFont.truetype("fonts/fontawesome.ttf", size=12)
        now = datetime.datetime.now()
        today_time = now.strftime("%H:%M")
        if today_time != today_last_time:
            with canvas(device) as draw:
                today_last_time = today_time
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

    #Runs when button is pressed
    @staticmethod
    def trigger():
        setScreen(1)

#Main menu (screenid: 1)
class mainmenu():
    @staticmethod
    def draw(device):
        global counter
        menu = ["Zurück", "Wiedergabe stoppen", "Radio", "gespeicherte Musik", "Ausschalten"]
        if counter != oldcounter and counter <= len(menu) and counter >= 0:
            oldcounter = counter
            with canvas(device) as draw:
                menuUsed(draw, menu)

        if counter > len(menu): counter = 0
        if counter < 0: counter = 0
    
    @staticmethod
    def trigger():
        global today_last_time
        global counter
        global activemenu
        if counter == 0: 
            today_last_time = "Unknown"
            activemenu = 0
        elif counter == 1:
            client.pause()
            today_last_time = "Unknown"
            activemenu = 0
            print("Playback stopped")
        elif counter == 2: setScreen(2)
        elif counter == 3: setScreen(4)
        elif counter == 4: setScreen(3)

#Shutdown menu (screenid: 3)
class shutdownmenu():
    @staticmethod
    def draw(device):
        menu = ["Wirklich herunterfahren?", "Nein", "Ja"]
        global counter
        if counter != oldcounter and counter <= len(menu) and counter >= 0:
            oldcounter = counter
            with canvas(device) as draw:
                menuUsed(draw, menu)

        if counter > len(menu): counter = 0
        if counter < 0: counter = 0
    @staticmethod
    def trigger():
        global counter
        if counter < 2: setScreen(1)
        elif counter == 2: shutdownSystem()

#Saved music (screenid: 4)
class savedmenu():
    @staticmethod
    def draw(device):
        menu = ["Zurück", "Musik starten", "Nächster Titel", "Vorheriger Titel"]
        global counter
        if counter != oldcounter and counter <= len(menu) and counter >= 0:
            oldcounter = counter
            with canvas(device) as draw:
                menuUsed(draw, menu)

        if counter > len(menu): counter = 0
        if counter < 0: counter = 0

    @staticmethod
    def trigger():
        global counter
        if counter == 0: setScreen(0)
        # elif counter == 1: offlineMusicPlay()
        # elif counter == 2: offlineMusicNext()
        # elif counter == 3: offlineMusicPrev()

#Radio station list (screenid: 2)
class radiomenu():
    @staticmethod
    def draw(device):
        global page
        global counter
        try:
            savedStations = client.listplaylistinfo("[Radio Streams]")
            menu = ["Zurück", ]
            for station in savedStations:
                menu.append(station["title"])
        except:
            setScreen(1) #TODO create error screen

        with canvas(device) as draw:
            if counter != oldcounter and counter <= len(menu) and counter >= 0:
                oldcounter = counter
                loadmenu = []
                for i in range(page, page + 5):
                    if len(menu) >= i + 1:
                        loadmenu.append(menu[i])
                menuUsed(draw, loadmenu)
            #Next page (scrolling)
            if page + counter > page + 3 and len(menu) > 5:
                page += 1
                counter -= 1
            if page + counter > len(menu):
                counter = 0
                page = 0
            if counter < 0: counter = 0

    @staticmethod
    def trigger():
        global counter
        if counter == 0: setScreen(1)
        elif counter != 0: playRadioStation(page + oldcounter -1)