#bouldererrr_ballroom
#Created by The Boulderer
#requires pip3, dotenv, youtube-dl, and discord installed on system
#sudo apt update
#pip3: sudo apt install python3-pip
#dotenv: pip install python-dotenv
#youtube-dl: sudo apt-get install youtube-dl
#discord: python3 -m pip install -U discord.py
#use this command to help with 403 errors: youtube-dl --rm-cache-dir
#ffmpeg should be placed in a adjacent folder
import time
import asyncio
import random
import os
import discord
from discord.ext import commands,tasks
from dotenv import load_dotenv
import youtube_dl

load_dotenv()

# Get Discord API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$',intents=intents)


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
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

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
#holds a list of active guildSongQue classes
guildlist = []



#add and remove sonQue class from guildlist array
def addGuild(x):
    guildlist.append(x)
    
def removeGuild(ctxid):
    for obj in guildlist:
        if ctxid == obj.guildid:
            guildlist.pop(guildlist.index(obj))
            
def checkGuild(ctxid):
    for g in guildlist:
        if g.guildid == ctxid:
            return True
        else:
            return False
            
def findGuild(ctxid):
    for g in guildlist:
        if g.guildid == ctxid:
            return g

#used to make saved song names more legible
def parseSongName(name):
    lastunder = name.rfind('_')
    firstsla = name.find('/')
    name = name[firstsla+1:lastunder]
    name = name.replace('_',' ')
    return name


#class manages songs for independent servers checks contextid against stored id to identify which class instance to use
class guildSongQue():
    def __init__(self, guildid):
        self.guildid = guildid
        self.songlist = []
        
        
    def addSong(self, filename):
        self.songlist.append(filename)
        
    def insertSong(self, location, filename):
        self.songlist.insert(location, filename)
    	
    def removeSong(self, filename):
        self.songlist.remove(filename)
   
    def popSong(self, pos):
        self.songlist.pop(pos)
        
    def clearSongs(self):
        l = len(self.songlist)
        for x in range(l):
            self.popSong(0)
    
    def getSong(self, pos):
        try:
    	    return self.songlist[pos]
        except:
    	    print("no songs in that position")

    #Plays a song in context server
    async def playSong(self, ctx):
        voice_client = ctx.message.guild.voice_client
        server = ctx.message.guild
        voice_channel = server.voice_client

        if len(self.songlist) > 0:
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg-static/ffmpeg", source=self.getSong(0)))
            print(parseSongName(self.getSong(0)))
            while (voice_client.is_playing() or voice_client.is_paused()):
                await asyncio.sleep(1)
            if len(self.songlist) > 0:
                self.popSong(0)
        
        return False
        
    
    
#youtubl class to download youtube audio file from links or search and return an array of filenames
class YTDLSource(discord.PCMVolumeTransformer):
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
            addGuild(guildSongQue(ctx.guild.id))
    except:
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
    except:
        await ctx.send("could not leave")






#Commands to manipulate sound track
@bot.command(name='play', help='plays a song from YouTube via url or search by name. \n'
            'Use quotations to search multiple words. Add shuffle to shuffle before playing \n'
            'example: $play "Song Name" \n'
            '$play playlist-url shuffle')
async def play(ctx, url, shuffle=None):

    #if not connected to a voice channel connect first
    if ctx.message.guild.voice_client == None:
        await join(ctx)
    
    server = ctx.message.guild
    voice_client = ctx.message.guild.voice_client
    voice_channel = server.voice_client
        
    #send url to YTDL to download and return a list of filesnames to be put into song que
    async with ctx.typing():
        filenames = await YTDLSource.from_url(url, loop=bot.loop)
        if shuffle == "shuffle":
            random.shuffle(filenames)
            
        g = findGuild(ctx.guild.id)
        
        for song in filenames:
            g.addSong(song)
            
    try:
        if voice_client.is_playing() or voice_client.is_paused():
            if voice_client.is_paused():
                await ctx.send("music player is paused")
            await ctx.send("Added to que")
        else:
            #voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg-static/ffmpeg", source=g.getSong(0)))
            sendstr = '**Now playing:** ' + parseSongName(g.getSong(0))
            await ctx.send(sendstr)
            while(len(g.songlist) > 0):
                if(await g.playSong(ctx)):
                    pass
                       
    except:
        await ctx.send("could not play song")


@bot.command(name='pause', help='Pauses the music player')
async def pause(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    except:
        await ctx.send("could not pause")
    
@bot.command(name='resume', help='Resumes player')
async def resume(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            await ctx.send("The bot is not playing anything. Use play command")
    except:
        await ctx.send("could not resume")

@bot.command(name='stop', help='Stops the player and clears song que')
async def stop(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing() or voice_client.is_paused():
            g = findGuild(ctx.guild.id)
            g.clearSongs()
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    except:
        await ctx.send("could not stop")



#que manipulation
@bot.command(name='add', help='Adds a song to the que. Works like play command')
async def add(ctx, url, shuffle=None):
    await play(ctx, url, shuffle)
        

@bot.command(name='clear', help='Clears the song que')
async def clear(ctx):
    try:
        g = findGuild(ctx.guild.id)
        tmp = g.getSong(0)
        g.clearSongs()
        g.addSong(tmp)
        await ctx.send("Song que cleared")
    except:
        await ctx.send("Could not clear the que")
    	
@bot.command(name='skip', help='Skips current song')
async def skip(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
                
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("Music player is not active")
    except:
    	await ctx.send("Could not skip")
        
        
        
@bot.command(name='playnext', help='Adds song(s) to play next in que')
async def playNext(ctx, url, shuffle=None):

    if ctx.message.guild.voice_client == None:
        await join(ctx)
        
    voice_client = ctx.message.guild.voice_client
    
    if voice_client.is_playing() == False and voice_client.is_paused() == False:
        await play(ctx, url, shuffle)
        return
    
    else:  
        async with ctx.typing():  
            filenames = await YTDLSource.from_url(url, loop=bot.loop)
            
            if shuffle == "shuffle":
                random.shuffle(filenames)
            g = findGuild(ctx.guild.id)
            
            c = 1
            for song in filenames:
                g.insertSong(c, song)
                c = c + 1
            await ctx.send("Playing song(s) next")
    
    
    
@bot.command(name='shuffle', help='Shuffles all songs in song que')
async def shuffle(ctx):
    async with ctx.typing():
        g = findGuild(ctx.guild.id)
        tmp = g.getSong(0)
        g.popSong(0)
        random.shuffle(g.songlist)
        g.insertSong(0, tmp)
        await ctx.send("Music que shuffled")
        
        
        
        
#informational commands
@bot.command(name='nowplaying', help='Names the currently playing song')
async def nowplaying(ctx):
    async with ctx.typing():
        g = findGuild(ctx.guild.id)
        await ctx.send(parseSongName(g.getSong(0)))

@bot.command(name='upnext', help='Lists the names of the next 10 songs in que')
async def upnext(ctx):
    async with ctx.typing():
        g = findGuild(ctx.guild.id)
        songs = ""
        c = 0
        for song in g.songlist:
            songs += parseSongName(song) + "\n"
            c = c+1
            if c > 9:
                break
        await ctx.send(songs)


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)
