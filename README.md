#Boulderer_Ballroom
#Author: TheBoulderer
#Discord Music Bot


requires pip3, dotenv, youtube-dl, discord, and ffmpeg to be installed on system

general package update:
sudo apt update
sudo apt upgrade

apt packages:
pip3: sudo apt install python3-pip
ffmpeg: sudo apt install ffmpeg

Create venv and install pip packages:
python3 -m venv .venv
source .venv/bin/activate

dotenv: python3 -m pip install python-dotenv
youtube-dl: python3 -m pip install --upgrade youtube-dl
discord: python3 -m install -U discord.py



Add your discord bot token to the .env file to connect to discord

use this command to help with youtube-dl 403 errors: youtube-dl --rm-cache-dir
Reinstall youtubedl: pip install --upgrade --force-reinstall "git+https://github.com/ytdl-org/youtube-dl.git"
