from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
import globalParameters

page = 0

#Radio station list (screenid: 2)
def draw(device, menu):
    global page
    counter = globalParameters.counter

    if counter != globalParameters.oldcounter and counter <= len(menu) and counter >= 0:
        globalParameters.oldcounter = counter
        with canvas(device) as draw:
            loadmenu = []
            for i in range(page, page + 5):
                if len(menu) >= i + 1:
                    loadmenu.append(menu[i])
            helperFunctions.drawMenu(draw, loadmenu)
    #Next page (scrolling)
    if page + counter > page + 3 and len(menu) > 5:
        page += 1
        globalParameters.counter -= 1
    if page + counter > len(menu):
        globalParameters.counter = 0
        page = 0
    if counter < 0: globalParameters.counter = 0

def trigger():
    counter = globalParameters.counter
    if counter == 0: helperFunctions.setScreen(1)
    elif counter != 0: 
        helperFunctions.playRadioStation(page+counter-1)