#Boulderer_Ballroom  
#Author: TheBoulderer  
#Discord Music Bot  
  
  
requires pip3, dotenv, and ffmpeg to be installed on system  

general package update:  
sudo apt update  
sudo apt upgrade  

apt packages:  
pip3: sudo apt install python3-pip  
ffmpeg: sudo apt install ffmpeg  


Environment Installs include Dotenv, yt-dlp, discord, and PyNacl

Create venv and install packages:  
python3 -m venv .venv  
source .venv/bin/activate  
  
dotenv: python3 -m pip install python-dotenv  
youtube-dl (possibly outdated use yt-dlp): python3 -m pip install --upgrade youtube-dl  
discord: python3 -m pip install -U discord.py  
PyNaCl: pip install PyNaCl
  
  
  
Add your discord bot token to the .env file to connect to discord  
  
use this command to help with youtube-dl 403 errors: youtube-dl --rm-cache-dir  
Reinstall youtubedl: pip install --upgrade --force-reinstall "git+https://github.com/ytdl-org/youtube-dl.git"  
