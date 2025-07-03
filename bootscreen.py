from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, time, socket, subprocess, requests
from homeassistant_api import Client

def boot(ver, hassurl, hassapi):
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
                ip = "IP: " + con.getsockname()[0]

                ssidresult = subprocess.run(
                    ["iwgetid", "-r"], capture_output=True, text=True, check=True
                )
            ssid = "WLAN: " + ssidresult.stdout.strip()
            booterror = 1
        except:
            ip = "0.0.0.0"
            ssid = "Fail to connect to Wifi"
            booterror = 0

        try:
            url = hassurl + "/api/config"
            token = hassapi

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                hassres = data.get('location_name') + " ist erreichbar"
                booterror = 1
            else:
                hassres = "Home Assistent ist nicht erreichbar!"
                booterror = 0
        except:
            hassres = "Home Assistent ist nicht erreichbar!"
            booterror = 0

        image_gen(epd, h, w, ver, ip, ssid, hassres, fortime, booterror)
   # except IOError as e:
    #    print("IOError:", e)
    except KeyboardInterrupt:
        epd.sleep()

def image_gen(epd,h, w, ver, ip, ssid, hassres, fortime, booterror):
    # create a image
    image = Image.new(mode='1', size=(h, w), color=255)
    draw = ImageDraw.Draw(image)

    #font things
    cat_font = ImageFont.truetype(font=os.path.join('/home/ingressy/mcat/RubikVinyl-Regular.ttf'), size=24)
    text_font = ImageFont.truetype(font=os.path.join('/home/ingressy/mcat/Roboto-Regular.ttf'), size=14)
    update_font = ImageFont.truetype(font=os.path.join('/home/ingressy/mcat/Roboto-Regular.ttf'), size=12)

    #draw image with text and stuff ~yeah
    draw.text((10, 10), f"m~cat {ver}", font=cat_font, fill=0, align='left')
    draw.text((10, 30), f"by ingressy", font=text_font, fill=0, align='left')
    draw.text((10, 60), f"{ip}", font=update_font, fill=0, align="left")
    draw.text((10, 70), f"{ssid}", font=update_font, fill=0, align="left")
    draw.text((10, 80), f"{hassres}", font=update_font, fill=0, align="left")
    draw.text((0, 110), f"last update: {fortime}", font=update_font, fill=0, align='left')

    # fix a "small" bug xD
    epd.init()

    # rotated_image = ImageOps.mirror(image)
    realimg = image.transpose(Image.FLIP_TOP_BOTTOM)
    roimg = ImageOps.mirror(realimg)
    epd.display(epd.getbuffer(roimg))
    epd.sleep()

    #check prg has a fail ...
    if booterror == 0:
        exit(0)
    time.sleep(5)
