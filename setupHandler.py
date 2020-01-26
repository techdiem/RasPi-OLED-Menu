#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
import globalParameters
import threading
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
import musicpd
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
    exit()

pingrun = threading.Event()
def asyncMPDPing():
    global client
    while not pingrun.is_set():
        try:
            client.ping()
        except:
            establishConnection()
        pingrun.wait(55)
    print("Ping thread exited.")

def startMPDPing():
    #create new thread for pinging MPD
    print("Create new thread for keeping the connection to MPD active")
    pingThread = threading.Thread(target=asyncMPDPing)
    pingThread.start()

mpdconnected = False
def establishConnectionHandler():
    global client, mpdconnected
    mpdretries = 0
    while not mpdconnected and mpdretries <= 5:
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
        sleep(4)
        mpdretries += 1

def establishConnection():
    global connectionThread, mpdconnected
    mpdconnected = False
    connectionThread = threading.Thread(target=establishConnectionHandler)
    connectionThread.start()
    connectionThread.join()
    if mpdconnected == False:
        print("Connection to MPD not possibe, Exiting...")
        screens.bigerror.draw(device, "MPD Verbindung unterbrochen!")
        sleep(10)

client = musicpd.MPDClient()
mpdconnected = False

def connectMPD():
    print("Connect to Mopidy")
    establishConnection()

def loadRadioPlaylist():
    global radiomenu
    try:
        client.clear()
        client.load("[Radio Streams]")
        globalParameters.loadedPlaylist = "[Radio Streams]"
        print("Loading radio stations")
        savedStations = client.listplaylistinfo("[Radio Streams]")
        radiomenu = ["Zurück", ]
        for station in savedStations:
            radiomenu.append(station['title'])
    except:
        establishConnection()

#Connect to MPD
connectMPD()
loadRadioPlaylist()

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

print("Setup finished")
print()
