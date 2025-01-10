import time, os, openmeteo_requests, requests_cache
from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
from retry_requests import retry

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
    weather_infos()

    draw.text((0,0), f"{temp}°C | {hum}% | {win}kn | {gus}kn | {dir}°", font=bar_font, fill=0, align='left')

def flash_image():
    #fix a "small" bug xD
    rotated_image = ImageOps.mirror(image)
    epd.display(epd.getbuffer(rotated_image))
    epd.sleep()

def weather_infos():

    global temp, hum, win, gus, dir

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 53.0451,
        "longitude": 8.8535,
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
        "wind_speed_unit": "kn"
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_wind_speed_10m = current.Variables(2).Value()
    current_wind_direction_10m = current.Variables(3).Value()
    current_wind_gusts_10m = current.Variables(4).Value()

    temp = round(current_temperature_2m, 2)
    hum = round(current_relative_humidity_2m, 2)
    win = round(current_wind_speed_10m, 2)
    gus = round(current_wind_gusts_10m, 2)
    dir = round(current_wind_direction_10m, 2)
