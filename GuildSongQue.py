#holds a list of active GuildSongQue classes
guildlist = []


#class manages songs for independent servers checks guildid to identify which class instance to use
class GuildSongQue():
    def __init__(self, guildid):
        self.guildid = guildid
        self.songlist = []
        self.shuffle = False
        
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
        except Exception as Argument:
            logging.exception("An Error occured in getSong function")
            print("no songs in that position")


        
    
#add, remove, and get GuildSongQue class from guildlist array
def addGuild(gsq):
    guildlist.append(gsq)
    
def removeGuild(ctxid):
    for obj in guildlist:
        if ctxid == obj.guildid:
            guildlist.pop(guildlist.index(obj))
            
def getGuild(ctxid):
    for g in guildlist:
        if g.guildid == ctxid:
            return g
            

