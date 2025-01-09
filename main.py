import json#,os, time, socket, subprocess
from bootscreen import boot
#from lib import epd2in13_V4
#from PIL import Image, ImageDraw, ImageFont, ImageOps

def main():
    try:
        #try to load the config.json file
        with open('config.json', 'r') as configfile:
            data = json.load(configfile)

            #load the config var
            ver = data["config"][0]["version"]

            #started the boot screen with the ver var
            boot(ver)

    except FileNotFoundError:
        #created the config.json file
        configfile = {"config": [
            {"version": "v0.2"}
        ]}
        with open('config.json', 'w') as file:
            json.dump(configfile, file, indent=4)

if __name__ == "__main__":
    main()
