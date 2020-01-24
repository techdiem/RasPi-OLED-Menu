from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
import datetime
from setupHandler import font_icons, font_text, font_clock, establishConnection

#assign inital values to variables
text_name = ""
text_position = 0
text_print = ""
playbackState = ""

#IDLE screen with clock and current playing song (screenid: 0)
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