import json
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

    except FileNotFoundError:
        #created the config.json file
        configfile = {"config": [
            {"version": "v0.3"}
        ]}
        with open('config.json', 'w') as file:
            json.dump(configfile, file, indent=4)

if __name__ == "__main__":
    main()
