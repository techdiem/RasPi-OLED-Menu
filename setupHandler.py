#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
from globalParameters import globalParameters, mediaVariables
import threading
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
import musicpd
from shairportmetadatareader import AirplayPipeListener
from time import sleep
import screens.bigerror
import screens.startscreen

#Setup OLED display
print("Connect to display")
device = sh1106(i2c(port=1, address=0x3C))
device.contrast(245)
screens.startscreen.draw(device) #User should have something to look at during start

#Set up rotary encoder
print("Set up rotary encoder")
clk = int(globalParameters.config.get('Pins', 'clk'))
dt = int(globalParameters.config.get('Pins', 'dt'))
sw = int(globalParameters.config.get('Pins', 'sw'))

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
current_clk = 1
current_dt = 1
LockRotary = threading.Lock() #create lock for rotary switch

def shutdown():
    #Cleanup GPIO connections
    GPIO.cleanup()
    pingrun.set()
    airplaylistener.stop_listening()
    exit()

client = musicpd.MPDClient()
pingrun = threading.Event()
def asyncMPDPing():
    while not pingrun.is_set():
        try:
            client.ping()
        except:
            establishConnection()
        pingrun.wait(55)
    print("Ping thread exited.")

def establishConnection():
    print("Connect to Mopidy")
    mpdconnected = False
    mpdretries = 0
    pingrun.set()
    while not mpdconnected and mpdretries <= 10:
        try: #Try a disconnect if the connection is in unknown state
            client.disconnect()
        except:
            pass
        try: #Try to reconnect
            client.connect(globalParameters.config.get('MPD', 'ip'), int(globalParameters.config.get('MPD', 'port')))
            print("MPD version", client.mpd_version)
            mpdconnected = True
        except:
            pass

        if mpdconnected == False:
            #Only sleep when no connection is avaiable -> faster startup
            sleep(5)
        mpdretries += 1
    if mpdconnected == False:
        print("Connection to MPD not possibe, Exiting...")
        screens.bigerror.draw(device, "MPD Verbindung unterbrochen!")
        sleep(10)
        exit()
    else:
        #create new thread for pinging MPD to keep connection up
        pingrun.clear()
        print("Creating new thread for keeping the connection to MPD active")
        pingThread = threading.Thread(target=asyncMPDPing)
        pingThread.start()

def loadRadioPlaylist():
    print("Loading radio stations")
    stations=["Zurück", ]
    try:
        playlistfile = open(globalParameters.config.get('General', 'stationsplaylist'),'r')
    except:
        print("Error loading radio stations: File does not exist, check your config file!")
        exit()

    #Check if it is a non-broken m3u8/m3u file
    line = playlistfile.readline()
    if not line.startswith('#EXTM3U'):
        print("Error loading radio stations: The m3u8 file is invalid!")
        exit()

    for line in playlistfile:
        line=line.strip()
        if line.startswith('#EXTINF:'):
            # EXTINF line with information about the station
            title=line.split('#EXTINF:')[1].split(',',1)[1]
            stations.append(title)

    playlistfile.close()
    mediaVariables.radiomenu = stations

    #Load playlist in Mopidy
    try:
        client.clear()
        client.load("[Radio Streams]")
    except:
        print("Error loading radio station playlist in Mopidy!")
        establishConnection()
        loadRadioPlaylist()

def loadPlaylists():
    print("Loading Subsonic and other playlists")
    try:
        mediaVariables.playlists = []
        clientplaylists = client.listplaylists()
        for playlist in clientplaylists:
            if playlist["playlist"] != "[Radio Streams]":
                mediaVariables.playlists.append(playlist["playlist"])
    except:
        print("Error loading playlists!")
        establishConnection()
        loadPlaylists()

#Connect to MPD
establishConnection()
loadRadioPlaylist()
loadPlaylists()

#Interrupt handler for push button in rotary encoder
def menuaction(channel):
    globalParameters.trigger = True

#Interrupt handler for turning the rotary encoder (changing the counter)
def rotary_detect(channel):  
    global current_clk, current_dt, LockRotary
    Switch_A = GPIO.input(clk)
    Switch_B = GPIO.input(dt)
    
    if current_clk == Switch_A and current_dt == Switch_B:
        #Same interrupt as before? -> Bouncing -> no action
        pass
    else:
        #refresh saved state
        current_clk = Switch_A
        current_dt = Switch_B
        
        if (Switch_A and Switch_B): #both ones active
            LockRotary.acquire()
            if channel == dt: #Direction depends on which one was last
                globalParameters.counter += 1
            else:
                globalParameters.counter -= 1 #Set Counter
            LockRotary.release()


print("Attaching interrupts")
#Rotary encoder
GPIO.add_event_detect(clk, GPIO.RISING, callback=rotary_detect)
GPIO.add_event_detect(dt, GPIO.RISING, callback=rotary_detect)
#Push Button
GPIO.add_event_detect(sw, GPIO.FALLING, callback=menuaction, bouncetime=300)

print("Connect to Shairport-Sync")
def on_airplay_track_info(lis, info):
    try:
        if client.status()['state'] == "play":
            print("Airplay connection detected, pausing Mopidy")
            client.pause()
    except:
        print("Error controlling Mopidy")
        establishConnection()
    mediaVariables.airplayinfo = info
    mediaVariables.loadedPlaylist = "[AirPlay]"

airplaylistener = AirplayPipeListener()
airplaylistener.bind(track_info=on_airplay_track_info)
airplaylistener.start_listening()

print("Setup finished")
print()
