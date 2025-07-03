import json, schedule, time
from bootscreen import boot
from dashboard import dash

def main():
    try:
        with open('/home/ingressy/mcat/config.json', 'r') as configjson:
            data = json.load(configjson)

            ver = data['config'][0]["version"]
            hassurl = data['config'][0]["hassurl"]
            hassapi = data['config'][0]['hassapi']

            print("Bootscreen wird geladen ...")
            boot(ver, hassurl, hassapi)
            print("Bootscreen wurde dargestellt ...")
            print("Dashboard wird geladen ...")
            dash()
            print("Dashboard wurde dargestellt ...")

            schedule.every().hour.at(":00").do(dash)
            schedule.every().hour.at(":15").do(dash)
            schedule.every().hour.at(":30").do(dash)
            schedule.every().hour.at(":45").do(dash)
        while True:
            schedule.run_pending()
            time.sleep(1)

    except FileNotFoundError:
        print("Fehler: config.json nicht gefunden")

if __name__ == "__main__":
    main()
