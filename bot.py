#Bouldererrr_Ballroom
#Created by TheBoulderer

import logging
import time
import asyncio
import random
import os
import discord
from discord.ext import commands,tasks
from dotenv import load_dotenv
import youtube_dl

from GuildSongQue import *

load_dotenv()

# Get Discord API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

#discord connection setup
intents = discord.Intents().all()
client = discord.Client(intents=intents)
#prefix can be any character but would recommend an uncommon symbol and one not used by other bots
bot = commands.Bot(command_prefix='%',intents=intents)


#youtube_dl setup
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'fragment_retries': 1,
    'restrictfilenames': True,
    'no-overwrites': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'outtmpl': 'playedsongs/%(title)s_%(id)s.%(ext)s'
}

#ffmpeg setup
ffmpeg_options = {
    'options': '-vn'
}

#global variables
#Set youtube_dl format options
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)  
    
#youtubl class to download youtube audio file from links or search and return an array of filenames
class YTDLSource(discord.PCMVolumeTransformer):
    try:
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = ""

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False):
            loop = loop or asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

            
            filename = []
            if 'entries' in data:
                for x in data['entries']:
                	filename.append(x['title'] if stream else ytdl.prepare_filename(x))
                return filename
            else:
                filename.append(data['title'] if stream else ytdl.prepare_filename(data))
                return filename
    except Exception as Argument:
        logging.exception("An error occured in YTDLSource function")
        

#Plays a song in context server
async def playSong(ctx):
    gsq = getGuild(ctx.guild.id)
    voice_client = ctx.message.guild.voice_client
    server = ctx.message.guild
    voice_channel = server.voice_client

    if len(gsq.songlist) > 0:
        voice_channel.play(discord.FFmpegPCMAudio(source=gsq.getSong(0)))
        print(parseSongName(gsq.getSong(0)))
        while (voice_client.is_playing() or voice_client.is_paused()):
            await asyncio.sleep(1)
        if len(gsq.songlist) > 0:
            gsq.popSong(0)
    
    return False


#Parse saved songs names to remove youtubeid and be more legible
def parseSongName(name):
    lastunderscore = name.rfind('_')
    firstslash = name.find('/')
    name = name[firstslash+1:lastunderscore]
    name = name.replace('_',' ')
    return name
    
    


#have the bot join or leave the channel
@bot.command(name='join', help='Join bot to current voice channel')
async def join(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return


        elif voice_client !=None:
            await ctx.send("Bot is already connected to a voice channel")
        
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            addGuild(GuildSongQue(ctx.guild.id))
            
    except Exception as Argument:
        logging.exception("An Error occured in join function")
        await ctx.send("could not join")



@bot.command(name='leave', help='Bot will leave the voice channel')
async def leave(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            if voice_client.is_playing() or voice_client.is_paused():
                await stop(ctx)
            await voice_client.disconnect()
            removeGuild(ctx.guild.id)

        else:
            await ctx.send("The bot is not connected to a voice channel.")
    except Exception as Argument:
        logging.exception("An Error occured in leave function")
        await ctx.send("could not leave")






#Commands to manipulate sound track
@bot.command(name='play', help='plays a song from YouTube via url or search by name. \n'
            'Will play from url or search by name \n'
            'example: $play song name \n'
            '$play playlist-url')
async def play(ctx, *argv):

    try:
        url = ""
        for item in argv:
            url += item + " "

        #if not connected to a voice channel connect first
        if ctx.message.guild.voice_client == None:
            await join(ctx)
        
        server = ctx.message.guild
        voice_client = ctx.message.guild.voice_client
        voice_channel = server.voice_client
            
        #send url to YTDL to download and return a list of filesnames to be put into song queue
        async with ctx.typing():
            filenames = await YTDLSource.from_url(url, loop=bot.loop)
            
            g = getGuild(ctx.guild.id)
            
            if g.shuffle == True:
                g.shuffle = False
                random.shuffle(filenames)
            
            for song in filenames:
                g.addSong(song)
            
    
        if voice_client.is_playing() or voice_client.is_paused():
            if voice_client.is_paused():
                await ctx.send("music player is paused")
            await ctx.send("Added song(s) to queue")
        else:
            sendstr = '**Now playing:** ' + parseSongName(g.getSong(0))
            await ctx.send(sendstr)
            while(len(g.songlist) > 0):
                if(await playSong(ctx)):
                    pass
                           
    except Exception as Argument:
        logging.exception("An error orrcured in play function")
        await ctx.send("could not play song")

@bot.command(name='playshuffled', help="plays songs and shuffles playlists on queing")
async def playShuffled(ctx, *argv):
    g = getGuild(ctx.guild.id)
    g.shuffle = True
    await play(ctx, *argv)


@bot.command(name='pause', help='Pauses the music player')
async def pause(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    except Exception as Argument:
        logging.exception("An Error occured in pause function")
        await ctx.send("could not pause")
    
@bot.command(name='resume', help='Resumes player')
async def resume(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            await ctx.send("The bot is not playing anything. Use play command")
    except Exception as Argument:
        logging.exception("An Error occured in resume function")
        await ctx.send("could not resume")

@bot.command(name='stop', help='Stops the player and clears song queue')
async def stop(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing() or voice_client.is_paused():
            g = getGuild(ctx.guild.id)
            g.clearSongs()
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    except Exception as Argument:
        logging.exception("An Error occured in stop function")
        await ctx.send("could not stop")



#queue manipulation
@bot.command(name='add', help='functions as play command')
async def add(ctx, *argv):
    await play(ctx, *argv)

@bot.command(name='addshuffled', help='functions as playshuffled command')
async def addShuffled(ctx, *argv):
    await playShuffled(ctx, *argv)
        

@bot.command(name='clear', help='Clears the song queue')
async def clear(ctx):
    try:
        g = getGuild(ctx.guild.id)
        tmp = g.getSong(0)
        g.clearSongs()
        g.addSong(tmp)
        await ctx.send("Song queue cleared")
    except Exception as Argument:
        logging.exception("An Error occured in clear function")
        await ctx.send("Could not clear the queue")
    	
@bot.command(name='skip', help='Skips current song')
async def skip(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
                
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("Music player is not active")
    except Exception as Argument:
        logging.exception("An Error occured in skip function")
        await ctx.send("Could not skip")
        
        
@bot.command(name='playnext', help='Adds song(s) to play next in queue')
async def playNext(ctx, *argv):

    url = ""
    for item in argv:
        url += item + " "

    if ctx.message.guild.voice_client == None:
        await join(ctx)
        
    voice_client = ctx.message.guild.voice_client
    
    if voice_client.is_playing() == False and voice_client.is_paused() == False:
        await play(ctx, url)
        return
    
    else:  
        async with ctx.typing():  
            filenames = await YTDLSource.from_url(url, loop=bot.loop)
            
            g = getGuild(ctx.guild.id)
            
            c = 1
            for song in filenames:
                g.insertSong(c, song)
                c = c + 1
            await ctx.send("Playing song(s) next")
    
    
@bot.command(name='shuffle', help='Shuffles all songs in song queue')
async def shuffle(ctx):
    async with ctx.typing():
        g = getGuild(ctx.guild.id)
        if ctx.message.guild.voice_client == None:
            await ctx.send("Bot is not connected to voice channel")
        elif len(g.songlist) == 0:
            await ctx.send("There are no songs in the queue")
        else:        
            tmp = g.getSong(0)
            g.popSong(0)
            random.shuffle(g.songlist)
            g.insertSong(0, tmp)
            await ctx.send("Music queue shuffled")
        
        
        
        
#informational commands
@bot.command(name='nowplaying', help='Names the currently playing song')
async def nowplaying(ctx):
    async with ctx.typing():
        g = getGuild(ctx.guild.id)
        if ctx.message.guild.voice_client == None:
            await ctx.send("Bot is not connected to voice channel")
        elif len(g.songlist) == 0:
            await ctx.send("There are no songs in the queue")
        else:
            await ctx.send(parseSongName(g.getSong(0)))

@bot.command(name='upnext', help='Lists the names of the next 10 songs in queue')
async def upnext(ctx):
    async with ctx.typing():
        g = getGuild(ctx.guild.id)
        if ctx.message.guild.voice_client == None:
            await ctx.send("Bot is not connected to voice channel")
        elif len(g.songlist) == 0:
            await ctx.send("There are no songs in the queue")
        else:
            songs = ""
            c = 0
            for song in g.songlist:
                songs += parseSongName(song) + "\n"
                c = c+1
                if c > 9:
                    break
            await ctx.send(songs)


if __name__ == "__main__" :
    logging.basicConfig(filename='bot.log', filemode='w', level=logging.INFO)
    logging.info('Started')
    bot.run(DISCORD_TOKEN)
    logging.info('Finished')
