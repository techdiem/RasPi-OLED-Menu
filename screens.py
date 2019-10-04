from PIL import ImageFont
##Imports for clock##
import datetime
####
from luma.core.render import canvas
import helperFunctions
from setupHandler import font_icons, font_text, font_clock

text_name = ""
text_position = 0
page = 0
today_last_time = "Unknown"
clock_last_time = "Unknown" #used for clock and song-name pulling

#IDLE screen with clock and current playing song (screenid: 0)
class idlescreen():
    #Used in main loop to create the screen
    @staticmethod
    def draw(device):
        global font_icons, font_clock, font_text
        global text_name, text_position
        global today_last_time, clock_last_time
        clockfont = ImageFont.truetype(font_clock, size=35)
        font = ImageFont.truetype(font_text, size=12)
        fontawesome = ImageFont.truetype(font_icons, size=12)
        now = datetime.datetime.now()
        today_time = now.strftime("%H:%M:%S")
        clock_time = now.strftime("%H:%M")

        if today_time != today_last_time:
            with canvas(device) as draw:
                today_last_time = today_time
                draw.text((20, 3), clock_time, font=clockfont, fill="white")

                #Currently playing song name
                if clock_time != clock_last_time:
                    clock_last_time = clock_time
                    try:
                        playingInfo = helperFunctions.client.currentsong()
                    except:
                        #connection lost -> restart
                        playingInfo = {'title': 'Could not load name!'}
                        helperFunctions.reconnect()
                    if playingInfo != {}:
                        currentSong = playingInfo["title"]
                        if currentSong != text_name:
                            text_name = currentSong
                            text_position = 0
                
                if text_name != "":
                    draw.text((0, 45), text="\uf001", font=fontawesome, fill="white") #music icon
                    if text_position < len(text_name):
                        draw.text((12, 48), text_name[text_position:], font=font, fill="white")
                        text_position += 1
                    else:
                        text_position = 0

    #Runs when button is pressed
    @staticmethod
    def trigger():
        helperFunctions.setScreen(1)

#Main menu (screenid: 1)
class mainmenu():
    @staticmethod
    def draw(device):
        global font_icons
        fontawesome = ImageFont.truetype(font_icons, size=18)
        counter = helperFunctions.counter
        if counter != helperFunctions.oldcounter and counter <= 4 and counter >= 0:
            helperFunctions.oldcounter = counter
            with canvas(device) as draw:
                #rectangle as selection marker
                if counter < 3: #currently 3 icons in one row
                    y = 2
                    x = 7 + counter * 35
                else:
                    y = 35
                    x = 6 + (counter - 3) * 35
                draw.rectangle((x, y, x+25, y+25), outline=255, fill=0)
                
                #icons as menu buttons
                draw.text((10, 5), text="\uf0a8", font=fontawesome, fill="white") #back
                draw.text((45, 5), text="\uf28d", font=fontawesome, fill="white") #stop
                draw.text((80, 5), text="\uf519", font=fontawesome, fill="white") #radio (old icon: f145)
                draw.text((10, 40), text="\uf019", font=fontawesome, fill="white") #saved music
                draw.text((45, 40), text="\uf011", font=fontawesome, fill="white") #shutdown
        
        #Keep the cursor in the screen
        if counter > 4: helperFunctions.counter = 0
        if counter < 0: helperFunctions.counter = 0
    
    @staticmethod
    def trigger():
        counter = helperFunctions.counter
        if counter == 0: 
            helperFunctions.setScreen(0)
        elif counter == 1:
            print("Playback stopped")
            helperFunctions.pausePlaying()
        elif counter == 2: helperFunctions.setScreen(2)
        elif counter == 3: helperFunctions.setScreen(4)
        elif counter == 4: helperFunctions.setScreen(3)

#Shutdown menu (screenid: 3)
class shutdownmenu():
    @staticmethod
    def draw(device):
        global font_text, font_icons
        font = ImageFont.truetype(font_text, size=12)
        fontawesome = ImageFont.truetype(font_icons, size=18)
        counter = helperFunctions.counter
        if counter != helperFunctions.oldcounter and counter <= 1 and counter >= 0:
            helperFunctions.oldcounter = counter
            with canvas(device) as draw:
                draw.text((5, 2), text="Wirklich ausschalten?", font=font, fill="white")
                if counter == 0:
                    x = 15
                    y = 22
                else:
                    x = 84
                    y = 22
                draw.rectangle((x, y, x+30, y+40), outline=255, fill=0)

                draw.text((18, 25), text="Nein", font=font, fill="white")
                draw.text((20, 40), text="\uf0a8", font=fontawesome, fill="white")

                draw.text((94, 25), text="Ja", font=font, fill="white")
                draw.text((90, 40), text="\uf011", font=fontawesome, fill="white")

        if counter > 1: helperFunctions.counter = 0
        if counter < 0: helperFunctions.counter = 0
    @staticmethod
    def trigger():
        counter = helperFunctions.counter
        if counter == 0: helperFunctions.setScreen(1)
        elif counter == 1: helperFunctions.shutdownSystem()

#Saved music (screenid: 4)
class savedmenu():
    @staticmethod
    def draw(device):
        menu = ["Zurück", "Musik starten", "Nächster Titel", "Vorheriger Titel"]
        counter = helperFunctions.counter
        if counter != helperFunctions.oldcounter and counter <= len(menu) and counter >= 0:
            helperFunctions.oldcounter = counter
            with canvas(device) as draw:
                helperFunctions.drawMenu(draw, menu)

        if counter > len(menu): helperFunctions.counter = 0
        if counter < 0: helperFunctions.counter = 0

    @staticmethod
    def trigger():
        counter = helperFunctions.counter
        if counter == 0: helperFunctions.setScreen(0)
        # elif counter == 1: offlineMusicPlay()
        # elif counter == 2: offlineMusicNext()
        # elif counter == 3: offlineMusicPrev()

#Radio station list (screenid: 2)
class radiomenu():
    @staticmethod
    def draw(device, menu):
        global page
        counter = helperFunctions.counter

        if counter != helperFunctions.oldcounter and counter <= len(menu) and counter >= 0:
            helperFunctions.oldcounter = counter
            with canvas(device) as draw:
                loadmenu = []
                for i in range(page, page + 5):
                    if len(menu) >= i + 1:
                        loadmenu.append(menu[i])
                helperFunctions.drawMenu(draw, loadmenu)
        #Next page (scrolling)
        if page + counter > page + 3 and len(menu) > 5:
            page += 1
            helperFunctions.counter -= 1
        if page + counter > len(menu):
            helperFunctions.counter = 0
            page = 0
        if counter < 0: helperFunctions.counter = 0

    @staticmethod
    def trigger():
        counter = helperFunctions.counter
        if counter == 0: helperFunctions.setScreen(1)
        elif counter != 0: 
            helperFunctions.playRadioStation(page + helperFunctions.counter -1)