#contains the YTDLSourse class

import youtube_dl
import discord

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
        
