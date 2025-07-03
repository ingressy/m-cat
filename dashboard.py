from datetime import datetime, timedelta
from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont, ImageOps
import time, os, requests, psutil, subprocess, json

def dash():
    global fontf, draw, epd, image, hassurl, hassapi, ver

    # display init
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    # width and height for image gen
    w = epd.width
    h = epd.height

    #create image
    image = Image.new(mode='1', size=(h, w), color=255)
    draw = ImageDraw.Draw(image)

    with open('/home/ingressy/mcat/config.json', 'r') as configfile:
        data = json.load(configfile)

        fontf = data["config"][0]["font-file"]
        hassurl = data['config'][0]["hassurl"]
        hassapi = data['config'][0]['hassapi']
        ver = data['config'][0]['version']

        weather()
        strom_krams()
        fenster()
        vbn()
        update_txt()
        sys_status()
        flash_image()

def weather():
    # Home Assistant URL und Token
    url =  hassurl + '/api/states/sensor.temperatur_luftfeuchtigkeit_zimmer_temperature'
    token = hassapi

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        temp = data['state'] + data['attributes']['unit_of_measurement']

    else:
        print('Fehler:', response.status_code, response.text)
        temp = "--°C"

    url = hassurl + '/api/states/sensor.temperatur_luftfeuchtigkeit_zimmer_humidity'

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        hum = data['state'] + data['attributes']['unit_of_measurement']

    else:
        print('Fehler:', response.status_code, response.text)
        hum = "--%"

        # Home Assistant URL und Token
    url = hassurl + '/api/states/sensor.garten_temp_temperature'
    token = hassapi

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        gtemp = data['state'] + data['attributes']['unit_of_measurement']

    else:
        print('Fehler:', response.status_code, response.text)
        gtemp = "--°C"

    url = hassurl + '/api/states/sensor.garten_temp_humidity'

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        ghum = data['state'] + data['attributes']['unit_of_measurement']

    else:
        print('Fehler:', response.status_code, response.text)
        ghum = "--%"

    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    draw.text((0, 0), f"Z: {temp} | {hum} || G: {gtemp} | {ghum} ", font=font, fill=0, align='left')

def strom_krams():
    # Home Assistant URL und Token
    url =  hassurl + '/api/states/sensor.gesamtleistung'
    token = hassapi

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        gewatt = data['state'] + data['attributes']['unit_of_measurement']

    else:
        print('Fehler:', response.status_code, response.text)
        gewatt = "0W"

    url = hassurl + '/api/states/sensor.insgesamte_stromstarke_zimmer'

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        gest = data['state'] + data['attributes']['unit_of_measurement']

    else:
        print('Fehler:', response.status_code, response.text)
        gest = "0A"


    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    draw.text((0, 12), f"Leistung: {gewatt} | Stromstärke: {gest}", font=font, fill=0, align='left')

def fenster():
    # Home Assistant URL und Token
    url =  hassurl + '/api/states/binary_sensor.badezimmerfenster_contact'
    token = hassapi

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        badezimmer = data['state']
        if badezimmer == "on":
            badezimmer = "auf"

    else:
        print('Fehler:', response.status_code, response.text)
        badezimmer = "n.a."

    url = hassurl + '/api/states/binary_sensor.kira_fenster_contact'

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        kira = data['state']
        if kira == "on":
            kira = "auf"

    else:
        print('Fehler:', response.status_code, response.text)
        kira = "n.a."

    url = hassurl + '/api/states/binary_sensor.jannik_zimmerfenster_contact'

    # Header mit Authentifizierung
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # API-Request senden
    response = requests.get(url, headers=headers)

    # Antwort prüfen und ausgeben
    if response.status_code == 200:
        data = response.json()
        jannik = data['state']
        if jannik == "on":
            jannik = "auf"

    else:
        print('Fehler:', response.status_code, response.text)
        jannik = "n.a."

    fenster = []
    if badezimmer == "auf":
        fenster.append(f"Badezimmer: {badezimmer}")
    if kira == "auf":
        fenster.append(f"Kira: {kira}")
    if jannik == "auf":
        fenster.append(f"Jannik: {jannik}")
    if not fenster:
        fenster.append("Kein Fenster offen!")

    txt = " | ".join(fenster)

    font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    draw.text((0, 24), txt, font=font, fill=0, align='left')

def vbn():
    # API-URL und Header
    token = ""
    url = "http://gtfsr.vbn.de/api/routers/default/index/stops/1:000009014131/stoptimes"
    headers = {
        "Authorization": token,
        "Host": "gtfsr.vbn.de"
    }

    # API-Anfrage senden
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        departures = []
        now = datetime.now()

        # Daten auswerten
        for entry in data:
            pattern = entry.get("pattern", {}).get("desc", "Unbekannte Linie")
            for time_entry in entry.get("times", []):
                service_day = time_entry.get("serviceDay", 0)
                realtime_departure = time_entry.get("realtimeDeparture", 0)

                # Berechnung der Abfahrtszeit
                departure_time = datetime.fromtimestamp(service_day) + timedelta(seconds=realtime_departure)

                # Nur Abfahrten in der Zukunft berücksichtigen
                if departure_time >= now:
                    formatted_time = departure_time.strftime("%H:%M:%S")
                    departures.append((pattern, departure_time, formatted_time))

        # Nach tatsächlicher Abfahrtszeit sortieren
        departures.sort(key=lambda x: x[1])

        # Sortierte Ausgabe der nächsten zwei Abfahrten
        font = ImageFont.truetype(font=os.path.join(fontf), size=12)
        if len(departures) >= 2:

            draw.text((0, 36), f"{departures[0][0]}, {departures[0][2]}", font=font, fill=0, align='left')
            #draw.text((0, 48), f"{departures[1][0]}, {departures[1][2]}", font=font, fill=0, align='left')
        elif len(departures) == 1:
            draw.text((0, 36), f"{departures[0][0]}, {departures[0][2]}", font=font, fill=0, align='left')
        else:
            draw.text((0, 36), f"Keine kommenden Abfahrten verfügbar.", font=font, fill=0, align='left')
    else:
        font = ImageFont.truetype(font=os.path.join(fontf), size=12)
        draw.text((0, 36), f"Keine kommenden Abfahrten verfügbar.", font=font, fill=0, align='left')

def update_txt():
    epd.init()

    ltime = time.localtime()
    fortime = time.strftime("%H:%M:%S | %d/%m/%Y", ltime)

    update_font = ImageFont.truetype(font=os.path.join(fontf), size=12)
    draw.text((0, 110), f"last update: {fortime}", font=update_font, fill=0, align='left')

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
        draw.text((0,95), f"new m~cat Version available | {ver}->{latest_version}", font=font, fill=0, align='left')
    else:
        if len(updates) > 1:
            draw.text((0,95), f"{cpu}% | {mem}% | {disk}% | Updates available", font=font, fill=0, align='left')
        else:
            draw.text((0,95), f"CPU: {cpu}% | MEM: {mem}% | DISK: {disk}%", font=font, fill=0, align='left')

def flash_image():
    # fix a "small" bug xD
    epd.init()

    # rotated_image = ImageOps.mirror(image)
    realimg = image.transpose(Image.FLIP_TOP_BOTTOM)
    roimg = ImageOps.mirror(realimg)
    epd.display(epd.getbuffer(roimg))
    #roimg.save("/home/ingressy/mcat/output.png")
    epd.sleep()
