#! /usr/bin/bash

echo "m~cat install script"
echo "v0.1"

# update system and python
sudo apt update && sudo apt -y upgrade && sudo apt install python3-pip python3-venv -y && sudo apt install --upgrade python3-setuptools

#setup venv
python3 -m venv env --system-site-packages

source env/bin/activate

