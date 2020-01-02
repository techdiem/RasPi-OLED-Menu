from PIL import ImageFont
##Imports for clock##
import datetime
####
from luma.core.render import canvas
import helperFunctions
from setupHandler import font_icons, font_text, font_clock, establishConnection, loadRadioPlaylist

#assign inital values to variables
text_name = ""
text_position = 0
text_print = ""
playbackState = ""
page = 0

#IDLE screen with clock and current playing song (screenid: 0)
class idlescreen():
    #Used in main loop to create the screen
    @staticmethod
    def draw(device):
        global font_icons, font_clock, font_text
        global text_name, text_position, text_print, playbackState
        clockfont = ImageFont.truetype(font_clock, size=30)
        font = ImageFont.truetype(font_text, size=12)
        faicons = ImageFont.truetype(font_icons, size=12)
        faiconsbig = ImageFont.truetype(font_icons, size=22)
        counter = helperFunctions.counter
        now = datetime.datetime.now()
        refresh_time = now.strftime("%H:%M:%S")
        clock_time = now.strftime("%H:%M")

        #runs every second (animations)
        if refresh_time != helperFunctions.today_last_time:
                helperFunctions.today_last_time = refresh_time
                #runs every minute (refresh, data gathering)
                if clock_time != helperFunctions.clock_last_time:
                    helperFunctions.clock_last_time = clock_time
                    
                    #Current playback state
                    try:
                        playbackInfo = helperFunctions.client.status()
                        playbackState = playbackInfo["state"]
                    except:
                        #connection lost -> restart
                        playingInfo = {'state': 'play'}
                        establishConnection()

                    #Currently playing song name
                    try:
                        playingInfo = helperFunctions.client.currentsong()
                    except:
                        #connection lost -> restart
                        playingInfo = {'title': 'Could not load name!'}
                        establishConnection()
                    if playingInfo != {}:
                        currentSong = playingInfo["title"]
                        if currentSong != text_name:
                            text_name = currentSong
                            text_position = 0
                #Rolling text for currently playing song
                if text_name != "":
                    text_print = text_name + "        " + text_name #8 spaces to create a nicer text flow
                    if text_position < len(text_name) + 8:
                        text_position += 1
                    else:
                        text_position = 0
        
        #Show all the data on the screen
        with canvas(device) as draw:
            #Current time
            draw.text((50, -10), clock_time, font=clockfont, fill="white")

            #Currently playing song
            if text_print != "":
                draw.text((0, 27), text="\uf001", font=faicons, fill="white") #music icon
                draw.text((12, 29), text_print[text_position:], font=font, fill="white")

            #Current music source and supported control buttons
            if helperFunctions.loadedPlaylist == "[Radio Streams]":
                controlElements = 1
                draw.text((3, 0), text="\uf519", font=faiconsbig, fill="white")#TODO: f1eb for airplay
            else:
                controlElements = 3
                draw.text((3, 0), text="\uf1c7", font=faiconsbig, fill="white")
                
            #Runs when rotary encoder is turned
            if counter != helperFunctions.oldcounter and counter <= controlElements and counter >= 0:
                #Selection rectangle
                if counter > 0:
                    x = 34+(counter-1)*20
                else:
                    x = 0
                y=48
                draw.rectangle((x, y, x+16, y+15), outline=255, fill=0)
                #Buttons
                draw.text((2, y+1), text="\uf187", font=faicons, fill="white") #menu
                if playbackState == "play":
                    draw.text((38, y), text="\uf04c", font=faicons, fill="white") #pause (f04b for play)
                else:
                    draw.text((38, y), text="\uf04b", font=faicons, fill="white") #play
                if controlElements == 3:
                    draw.text((57, y+1), text="\uf04a", font=faicons, fill="white") #previous
                    draw.text((78, y+1), text="\uf04e", font=faicons, fill="white") #next
            #Keep the cursor in the screen
            if counter > controlElements: helperFunctions.counter = 0
            if counter < 0: helperFunctions.counter = 0

    #Runs when button is pressed
    @staticmethod
    def trigger():
        global playbackState
        counter = helperFunctions.counter
        if counter == 0: helperFunctions.setScreen(1)
        elif counter == 1: 
            if playbackState == "play": 
                helperFunctions.playbackControl("pause")
            else: 
                helperFunctions.playbackControl("play")
        elif counter == 2: helperFunctions.playbackControl("previous")
        elif counter == 3: helperFunctions.playbackControl("next")

#Main menu (screenid: 1)
class mainmenu():
    @staticmethod
    def draw(device):
        global font_icons
        faicons = ImageFont.truetype(font_icons, size=18)
        counter = helperFunctions.counter
        if counter != helperFunctions.oldcounter and counter <= 3 and counter >= 0:
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
                draw.text((10, 5), text="\uf0a8", font=faicons, fill="white") #back
                draw.text((45, 5), text="\uf519", font=faicons, fill="white") #radio (old icon: f145)
                draw.text((80, 5), text="\uf1c7", font=faicons, fill="white") #playlists
                draw.text((10, 40), text="\uf011", font=faicons, fill="white") #shutdown
        
        #Keep the cursor in the screen
        if counter > 3: helperFunctions.counter = 0
        if counter < 0: helperFunctions.counter = 0
    
    @staticmethod
    def trigger():
        counter = helperFunctions.counter
        if counter == 0: helperFunctions.setScreen(0)
        elif counter == 1: 
            if helperFunctions.loadedPlaylist != "[Radio Streams]":
                loadRadioPlaylist()
            helperFunctions.setScreen(2)
        elif counter == 2: 
            helperFunctions.loadPlaylists()
            helperFunctions.setScreen(4)
        elif counter == 3: helperFunctions.setScreen(3)

#Shutdown menu (screenid: 3)
class shutdownmenu():
    @staticmethod
    def draw(device):
        global font_text, font_icons
        font = ImageFont.truetype(font_text, size=12)
        faicons = ImageFont.truetype(font_icons, size=18)
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
                draw.text((20, 40), text="\uf0a8", font=faicons, fill="white")

                draw.text((94, 25), text="Ja", font=font, fill="white")
                draw.text((90, 40), text="\uf011", font=faicons, fill="white")

        if counter > 1: helperFunctions.counter = 0
        if counter < 0: helperFunctions.counter = 0
    @staticmethod
    def trigger():
        counter = helperFunctions.counter
        if counter == 0: helperFunctions.setScreen(1)
        elif counter == 1: helperFunctions.shutdownSystem()

#Saved music (screenid: 4)
class playlistmenu():
    @staticmethod
    def draw(device):
        global page
        menu = helperFunctions.playlists
        counter = helperFunctions.counter
        menu = ["Zurück"] + menu
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
        menu = helperFunctions.playlists
        if counter == 0: 
            helperFunctions.setScreen(0)
        else:
            helperFunctions.loadPlaylist(menu[page+counter-1])
            helperFunctions.setScreen(0)


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
            helperFunctions.playRadioStation(page+counter-1)