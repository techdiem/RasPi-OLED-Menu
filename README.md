# RasPi-OLED-Menu

## My use
This code is for a homemade internet radio.
It is based on a Raspberry Pi Zero W with a USB sound card.
Only controllable via a web interface was no option for me, so I added a small OLED display and a rotary encoder.
There should be a menu to navigate through with the rotary encoder.
The controller chip of the little oled is the sh1106. (I bought it from ebay)

## Installation
The code is based on the luma.oled library.
To install it, just follow the instruction [in the luma.oled documentation](https://luma-oled.readthedocs.io/en/latest/install.html). This example is written in python3, so please use python3, pip3 and so on.
To use it, connect your display (there are lots of guides online), and start it using ``` python3 oled.py ```


## Some important information about the project
Currently, the code is very buggy, it crashes sometimes, mainly caused by the connection to Mopidy (MPD).
I just wrote it very quickly, because the hardware was assembled and I wanted to test it... :P
But I will look into this at some time, because it runs on my radio and I don't want it to just occasionally crash as it is the main way to control the device :D
I configured it as a systemd service, which autostarts the software on system boot and restarts the oled after 15 seconds when it crashed, but thats just a bad workaround :P.

New features will be added at some time after the bugs are fixed and the code is cleaned...
