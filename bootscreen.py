from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, time, socket, subprocess

def boot():
    booterror = 0
    try:
        epd = epd2in13_V4.EPD()
        epd.init()
        epd.Clear(0xFF)

        w = epd.width
        h = epd.height

        epd.init()
        image = Image.new(mode='1', size=(h, w), color=255)
        draw = ImageDraw.Draw(image)

        big_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=18)
        text_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=14)
        update_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)

        ltime = time.localtime()
        fortime = time.strftime("%H:%M:%S,%d/%m/%Y", ltime)

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

        draw.text((10, 10), f"m~cat v0.2", font=big_font, fill=0, align='left')
        draw.text((10, 30), f"by ingressy", font=text_font, fill=0, align='left')
        draw.text((10, 60), f"{ip}", font=update_font, fill=0, align="left")
        draw.text((10, 80), f"{ssid}", font=update_font, fill=0, align="left")
        draw.text((0, 110), f"last update: {fortime}", font=update_font, fill=0, align='left')
        rotated_image = ImageOps.mirror(image)

        epd.display(epd.getbuffer(rotated_image))
        epd.sleep()

        if booterror == 0:
            exit(0)
        time.sleep(5)

    except IOError as e:
        print("IOError:", e)
    except KeyboardInterrupt:
        epd.sleep()
