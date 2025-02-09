import json, time, schedule, logging
from bootscreen import boot
from dashboard import dash

def main():
    try:
        #try to load the config.json file
        with open('/home/ingressy/mcat/code/config.json', 'r') as configfile:
            data = json.load(configfile)

            #load the config var
            ver = data["config"][0]["version"]
            
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Starting m-cat")

            #started the boot screen with the ver var
            boot(ver)

            logging.debug("displaying bootscreen")

            dash()
            logging.debug("displaying dashboard")

            #schedule every day
            schedule.every().hour.at(":00").do(dash)
            schedule.every().hour.at(":15").do(dash)
            schedule.every().hour.at(":30").do(dash)
            schedule.every().hour.at(":45").do(dash)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except FileNotFoundError:
        #created the config.json file
        configfile = {"config": [
            {"version": "v0.6.1", "webinterface": "true",
            "font-file": "/home/ingressy/mcat/code/Roboto-Regular.ttf"},
            {"latitude": "53.0451", "longitude": "8.8535"},
            {"birthday_month": "3", "birthday_day": "9"},
            {"untisenable": "true", "server": "https://tipo.webuntis.com", "username": "dummy3",
             "password": "NewShit24!", "school": "TBZ Mitte Bremen",
             "useragent": "dummy3", "class": "BGT 241"}
        ]}
        with open('/home/ingressy/mcat/code/config.json', 'w') as file:
            json.dump(configfile, file, indent=4)

if __name__ == "__main__":
    main()
