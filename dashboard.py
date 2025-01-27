import time, os, openmeteo_requests, requests_cache, psutil, json, re
from datetime import datetime, timedelta
from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
from retry_requests import retry

def dash():
    global epd, h, w, image, draw, data
    # display init
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    # width and height for image gen
    w = epd.width
    h = epd.height

    image = Image.new(mode='1', size=(h, w), color=255)
    draw = ImageDraw.Draw(image)

    #try:
    with open('config.json', 'r') as configfile:
        data = json.load(configfile)

        status_bar()
        tide()
        time_things()
        sys_status()
        update_text()

        flash_image()
    #except:
       # print("Configfile not found !")
       # exit(0)

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
    bar_font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)
    weather_infos()

    draw.text((0,0), f"{temp}°C | {hum}% | {win}kn | {gus}kn | {dir}°", font=bar_font, fill=0, align='left')
    draw.text((0, 12), f"{atemp}°C | rain: {rai}mm | snow: {sno}cm", font=bar_font, fill=0, align='left')

def flash_image():
    #fix a "small" bug xD
    epd.init()

    rotated_image = ImageOps.mirror(image)
    epd.display(epd.getbuffer(rotated_image))
    epd.sleep()

def weather_infos():

    global temp, hum, win, gus, dir, atemp, rai, sno

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": data["config"][0]["latitude"],
        "longitude": data["config"][0]["longitude"],
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "rain", "snowfall", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
        "wind_speed_unit": "kn"
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    current_rain = current.Variables(3).Value()
    current_snowfall = current.Variables(4).Value()
    current_wind_speed_10m = current.Variables(5).Value()
    current_wind_direction_10m = current.Variables(6).Value()
    current_wind_gusts_10m = current.Variables(7).Value()

    temp = round(current_temperature_2m, 2)
    hum = round(current_relative_humidity_2m, 2)
    win = round(current_wind_speed_10m, 2)
    gus = round(current_wind_gusts_10m, 2)
    dir = round(current_wind_direction_10m, 2)
    atemp = round(current_apparent_temperature, 2)
    rai = round(current_rain, 2)
    sno = round(current_snowfall, 2)

def sys_status():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()[2]
    disk = psutil.disk_usage('/')[3]

    font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)
    draw.text((0,95), f"CPU: {cpu}% | MEM: {mem}% | DISK: {disk}%", font=font, fill=0, align='left')

def time_things():
    birthday_month =  int(data["config"][0]["birthday_month"])
    birthday_day = int(data["config"][0]["birthday_day"])
    total_sec_in_day = 86400

    today = datetime.today()
    current_year = datetime.now().year
    now = datetime.now()

    sec_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
    start_of_year = datetime(current_year, 1,1)
    end_of_year = datetime(current_year + 1,1,1)
    total_secounds = (end_of_year - start_of_year).total_seconds()
    elapsed_secounds = (now - start_of_year).total_seconds()

    percentage = round(((elapsed_secounds / total_secounds)* 100), 2)
    daypercentage = round(((sec_since_midnight / total_sec_in_day) * 100),2)

    if today.month > birthday_month or (today.month == birthday_month and today.day > birthday_day):
        birthday_year = today.year +1
    else:
        birthday_year = today.year
    birthday = datetime(birthday_year, birthday_month, birthday_day)
    birthdate = (birthday - today).days

    font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)
    draw.text((0, 71), f"{percentage}% of the year | {daypercentage}% of the day", font=font, fill=0, align='left')
    draw.text((0, 83), f"Birthday in {birthdate} Day(s)", font=font, fill=0, align='left')

def adjust_time_for_dst(date_str, time_str):
    date = datetime.strptime(date_str, "%d. %m.%Y")

    year = date.year
    start_dst = datetime(year, 3, (31 - (datetime(year, 3, 31).weekday() + 1) % 7), 2)
    end_dst = datetime(year, 10, (31 - (datetime(year, 10, 31).weekday() + 1) % 7),3)

    if start_dst <= date < end_dst:
        time = datetime.strptime(time_str, "%H:%M")
        time += timedelta(hours=1)

        if time.day > date.day:
            return time.strftime("%H:%M")
        else:
            return time.strftime("%H:%M")
    return time_str

def tide():
    with open("tide.txt", "r") as file:
        data = file.read()

    pattern = r"#([NH])#\w{2}#\s*(\d+\.\s*\d+\.\s*\d{4})#\s*(\d{1,2}:\d{2})#"

    results = re.findall(pattern, data)
    now = datetime.now()
    today = now.strftime("%-d. %-m.%Y")

    filtered_results = []
    for typ, date, time in results:
        date = date.strip()
        if date == today:
            time = adjust_time_for_dst(date, time)
            filtered_results.append((typ, time))

    h_times = [time for typ, time in filtered_results if typ == "H"]
    n_times = [time for typ, time in filtered_results if typ == "N"]

    h_times_str = ", ".join(h_times) if h_times else "Keine"
    n_times_str = ", ".join(n_times) if n_times else "Keine"

    font = ImageFont.truetype(font=os.path.join('Roboto-Regular.ttf'), size=12)
    draw.text((0, 59), f"HW: {h_times_str} | NW: {n_times_str}", font=font, fill=0, align='left')
