import json, time, schedule
from bootscreen import boot
from dashboard import dash

def main():
    try:
        #try to load the config.json file
        with open('config.json', 'r') as configfile:
            data = json.load(configfile)

            #load the config var
            ver = data["config"][0]["version"]

            #started the boot screen with the ver var
            boot(ver)
            dash()

            #schedule every day
            schedule.every().day.at("00:00").do(dash)
            schedule.every().day.at("05:00").do(dash)
            schedule.every().day.at("06:00").do(dash)
            schedule.every().day.at("07:00").do(dash)
            schedule.every().day.at("08:00").do(dash)
            schedule.every().day.at("09:00").do(dash)
            schedule.every().day.at("10:00").do(dash)

            schedule.every().day.at("12:00").do(dash)
            schedule.every().day.at("15:00").do(dash)
            schedule.every().day.at("17:00").do(dash)

            schedule.every().day.at("19:00").do(dash)
            schedule.every().day.at("20:00").do(dash)
            schedule.every().day.at("21:00").do(dash)
            schedule.every().day.at("22:00").do(dash)
            schedule.every().day.at("23:00").do(dash)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except FileNotFoundError:
        #created the config.json file
        configfile = {"config": [
            {"version": "v0.5", "latitude": "0", "longitude": "0", "birthday_month": "1", "birthday_day": "1"}
        ]}
        with open('config.json', 'w') as file:
            json.dump(configfile, file, indent=4)

if __name__ == "__main__":
    main()
