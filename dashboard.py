import time, os, openmeteo_requests, requests_cache, psutil, json, re, webuntis, requests, subprocess
from datetime import datetime, timedelta
from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
from retry_requests import retry

def dash():
    global epd, h, w, image, draw, data, fontf, ver
    # display init
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    # width and height for image gen
    w = epd.width
    h = epd.height

    image = Image.new(mode='1', size=(h, w), color=255)
    draw = ImageDraw.Draw(image)

    with open('/home/ingressy/mcat/code/config.json', 'r') as configfile:
        data = json.load(configfile)
        ver = data["config"][0]["version"]
        fontf = data["config"][0]["font-file"]
        untisenable = data["config"][3]["untisenable"]

        status_bar()
        people_in_sky()
        if untisenable == "true":
            untis()
        tide()
        time_things()
        sys_status()
        update_text()

        flash_image()
def update_text():
    global rotated_image

    # re init | because idk
    epd.init()

    # time handling
    ltime = time.localtime()
    fortime = time.strftime("%H:%M:%S | %d/%m/%Y", ltime)

    update_font = ImageFont.truetype(font=os.path.join(fontf), size=12)

    draw.text((0, 110), f"last update: {fortime}", font=update_font, fill=0, align='left')

def status_bar():
    bar_font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    weather_infos()

    draw.text((0,0), f"{temp}°C | {hum}% | {win}kn | {gus}kn | {dir}°", font=bar_font, fill=0, align='left')
    draw.text((0, 12), f"{atemp}°C | rain: {rai}mm | snow: {sno}cm", font=bar_font, fill=0, align='left')

def people_in_sky():
    # API-Endpunkt für die Anzahl der Menschen im All
    url = "http://api.open-notify.org/astros.json"

    # Abrufen der Daten
    response = requests.get(url)
    data = response.json()

    # Ausgabe der aktuellen Anzahl der Menschen im All
    print(f"Es sind derzeit {data['number']} Menschen im All.")

    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    draw.text((0, 35), f"{data['number']} Menschen sind im All", font=font, fill=0,align='left')
def flash_image():
    # fix a "small" bug xD
    epd.init()

    # rotated_image = ImageOps.mirror(image)
    realimg = image.transpose(Image.FLIP_TOP_BOTTOM)
    roimg = ImageOps.mirror(realimg)
    epd.display(epd.getbuffer(roimg))
    epd.sleep()

def untis():
    s = webuntis.Session(
        server=data["config"][3]["server"],
        username=data["config"][3]["username"],
        password=data["config"][3]["password"],
        school=data["config"][3]["school"],
        useragent=data["config"][3]["useragent"]
    )
    s.login()

    start = datetime.now()
    end = start + timedelta(days=6)
    time = datetime.now()
    chtime = (time.strftime("%H%M"))
    cache = []

    klasse = s.klassen().filter(name=data["config"][3]["class"])
    tt = s.timetable(klasse=klasse[0], start=start, end=end)
    tt = sorted(tt, key=lambda x: x.start)

    time_format_date = "%Y-%m-%d"
    time_format_end = "%H%M"
    time_format_start = time_format_end
    time_start = "%H:%M"
    time_end = "%H:%M"

    for po in tt:
        d = po.start.strftime(time_format_date)
        s = po.start.strftime(time_format_start)
        sf = po.start.strftime(time_start)
        e = po.end.strftime(time_format_end)
        ef = po.end.strftime(time_end)
        k = " ".join([k.name for k in po.klassen])
        try:
            t = " ".join([t.name for t in po.teachers])
        except IndexError:
            t = "--"
        r = " ".join([r.name for r in po.rooms])
        sub = " ".join([r.name for r in po.subjects])
        c = "(" + po.code + ")" if po.code is not None else ""

        cache.append(d)
        cache.append(s)
        cache.append(sf)
        cache.append(e)
        cache.append(ef)
        cache.append(t)
        cache.append(r)
        cache.append(sub)
        cache.append(c)


        for i in range(0, len(cache), 9):
            datum = cache[i]
            datumkurz = datum[5:]
            datumkurz = ".".join(datumkurz.split("-")[::-1])
            endtime = cache[i + 3]
            etime = cache[i + 4]

            #starttime = cache[i + 1]
            stime = cache[i + 2]
            teacher = cache[i + 5]
            room = cache[i + 6]
            subject = cache[i + 7]
            can = cache[i + 8]

            if datum == datetime.today().strftime("%Y-%m-%d"):
                if endtime >= chtime:
                    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
                    if room is None or not room.strip():
                        room = "---"
                    if subject is None or not subject.strip():
                        subject = "---"
                    draw.text((0, 47),f"{stime} - {etime} | {teacher} | {room} | {subject}  | {can}", font=font, fill=0, align='left')
                    break
            else:
                font = ImageFont.truetype(font=os.path.join(fontf), size=12)
                if room is None or not room.strip():
                    room = "---"
                if subject is None or not subject.strip():
                    subject = "---"
                draw.text((0, 47), f"{datumkurz} | {stime} - {etime} | {teacher} | {room} | {subject}  | {can}", font=font, fill=0, align='left')
                break
def weather_infos():

    global temp, hum, win, gus, dir, atemp, rai, sno

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": data["config"][1]["latitude"],
        "longitude": data["config"][1]["longitude"],
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
    #check system updates
    result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True)
    updates = result.stdout.strip().split("\n")

    #new mcat version check
    url = f"https://api.github.com/repos/ingressy/m-cat/tags"
    response = requests.get(url)

    if response.status_code == 200 and response.json():
        latest_version = response.json()[0]["name"]
        if latest_version != ver:
            newver = 1
        else:
            newver = 0
    else:
        newver = 0

    #sys stats
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()[2]
    disk = psutil.disk_usage('/')[3]

    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    if newver == 1:
        draw.text((0,95), f"new m~cat Version available | {latest_version}", font=font, fill=0, align='left')
    else:
        if len(updates) > 1:
            draw.text((0,95), f"{cpu}% | {mem}% | {disk}% | Updates available", font=font, fill=0, align='left')
        else:
            draw.text((0,95), f"CPU: {cpu}% | MEM: {mem}% | DISK: {disk}%", font=font, fill=0, align='left')

def time_things():
    birthday_month =  int(data["config"][2]["birthday_month"])
    birthday_day = int(data["config"][2]["birthday_day"])
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

    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
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
    with open("/home/ingressy/mcat/code/tide.txt", "r") as file:
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

    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    draw.text((0, 59), f"HW: {h_times_str} | NW: {n_times_str}", font=font, fill=0, align='left')
