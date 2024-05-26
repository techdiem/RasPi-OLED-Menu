"""
Software settings
"""

STATIONSPLAYLIST = "/music/playlists/[Radio Streams].m3u8"
EMULATED = False

#Pins for rotary encoder
PIN_CLK = 17
PIN_DT = 18
PIN_SW = 27

#ADS1115 I2C for potentiometer
ADS_I2C = 0x48

#Alsa output for volume control
ALSA_CARD = "hw:1"
ALSA_MIXER = "Stereo"

#Settings for the connection to Mopidy
MPD_IP = "localhost"
MPD_PORT = 6600

#Font files (TrueType)
FONT_ICONS = "fonts/fontawesome.otf"
FONT_TEXT = "fonts/arial.ttf"
FONT_CLOCK = "fonts/calibri.ttf"
