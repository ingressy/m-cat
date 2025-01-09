from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, time, socket, subprocess

def boot(ver):
    #set boot error of nil
    booterror = 0

    try:
        #display init
        epd = epd2in13_V4.EPD()
        epd.init()
        epd.Clear(0xFF)

        #width and height for image gen
        w = epd.width
        h = epd.height

        #re init | because idk
        epd.init()

        #time handling
        ltime = time.localtime()
        fortime = time.strftime("%H:%M:%S | %d/%m/%Y", ltime)

        #test internet connection
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as con:
                con.connect(("8.8.8.8", 80))
                ip = con.getsockname()[0]

                ssidresult = subprocess.run(
                    ["iwgetid", "-r"], capture_output=True, text=True, check=True
                )
            ssid = ssidresult.stdout.strip()
            booterror = 1
        except:
            ip = "0.0.0.0"
            ssid = "Fail to connect to Wifi"
            booterror = 0

        image_gen(epd, h, w, ver, ip, ssid, fortime, booterror)

    except IOError as e:
        print("IOError:", e)
    except KeyboardInterrupt:
        epd.sleep()

def image_gen(epd,h, w, ver, ip, ssid, fortime, booterror):
    # create a image
    image = Image.new(mode='1', size=(h, w), color=255)
    draw = ImageDraw.Draw(image)

    #font things
    big_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=18)
    text_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=14)
    update_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)

    #draw image with text and stuff ~yeah
    draw.text((10, 10), f"m~cat {ver}", font=big_font, fill=0, align='left')
    draw.text((10, 30), f"by ingressy", font=text_font, fill=0, align='left')
    draw.text((10, 60), f"{ip}", font=update_font, fill=0, align="left")
    draw.text((10, 80), f"{ssid}", font=update_font, fill=0, align="left")
    draw.text((0, 110), f"last update: {fortime}", font=update_font, fill=0, align='left')

    #fix a "small" bug xD
    rotated_image = ImageOps.mirror(image)

    #display image and display goes sleeping
    epd.display(epd.getbuffer(rotated_image))
    epd.sleep()

    #check prg has a fail ...
    if booterror == 0:
        exit(0)
    time.sleep(5)
