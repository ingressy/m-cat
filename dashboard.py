import time, os
from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps

def dash():
    global epd, h, w, image, draw
    # display init
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    # width and height for image gen
    w = epd.width
    h = epd.height

    image = Image.new(mode='1', size=(h, w), color=255)
    draw = ImageDraw.Draw(image)

    update_text()
    status_bar()

    flash_image()


def update_text():
    global rotated_image

    # re init | because idk
    epd.init()

    # time handling
    ltime = time.localtime()
    fortime = time.strftime("%H:%M:%S | %d/%m/%Y", ltime)

    update_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)

    draw.text((0, 110), f"last update: {fortime}", font=update_font, fill=0, align='left')

def status_bar():
    epd.init()
    bar_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)

    draw.text((0,0), "~meow", font=bar_font, fill=0, align='left')

def flash_image():
    #fix a "small" bug xD
    rotated_image = ImageOps.mirror(image)
    epd.display(epd.getbuffer(rotated_image))
    epd.sleep()
