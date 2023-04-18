import discord
import sqlite3
import pathlib
import Commands.commandcontroller
import vars

botSettings = vars.getSettings()

def setup():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = ArmoryBot(intents=intents)
    bot.run(botSettings["token"])



class ArmoryBot(discord.Client):

    def __init__(self, *, intents, **options) -> None:
        super().__init__(intents=intents, **options)
        
        self.items = {}
        self.db = Database()
        self.prefixes = {}
        self.defaultRealm = {}
        #Don't need to load roles etc. into memory, because those will be rarely hit.



    

    async def getWarmaneData():
        # 1) HTTP request to warmane armory, dont care about API
        # 2) Parse XHTML
        # 3) Return data
        parsedData = []
        successCode = 1 or 0
        # return data[parsedData] #if data was successfully parsed and queried, we return data, otherwise empty array
        NotImplementedError


    async def on_ready(self):
        #loading into memory, because memory load will be neligible from 32k records. (Entire program takes about 100mb memory)
        #

        response = self.db.query("SELECT guild_snowflake, prefix, realm FROM guild")
        for prefix in response:
            self.prefixes[prefix[0]] = prefix[1]
            self.defaultRealm[prefix[0]] = prefix[2]

        items = self.db.query("SELECT GearScore, ItemLevel, class, gems, ItemID, name, quality, requires, subclass, type FROM items")
        for item in items:
            self.items[item[4]] = {
                                    "gs" : item[0],
                                   "ilvl" : item[1],
                                   "class" : item[2],
                                   "gems" : item[3],
                                   "name" : item[5],
                                   "quality" : item[6],
                                   "requires" : item[7],
                                   "sublcass" : item[8],
                                   "type" : item[9]
                                   }
        
        print(len(self.items))
        print(f'Logged on as {self.user}!')

    async def on_guild_join(self, guild):
        self.db.query("INSERT INTO guild (guild_snowflake, realm, prefix) VALUES ({snowflake}, '{realm}', '{prefix}')"
                      .format(snowflake = guild.id, realm = "Icecrown", prefix = ".wm"))
        self.db.commit()
        self.prefixes[guild.id] = ".wm"
    async def on_guild_remove(self, guild):
        self.db.query("DELETE FROM guild WHERE guild_snowflake = {snowflake}"
                      .format(snowflake = guild.id))

    async def getPrefix(self, message) -> bool:
        if message.guild == None:
            return ".bot"
        else: 
            return self.prefixes[message.guild.id]
        
    async def getDefaultRealm(self, message) -> bool:
        if message.guild == None:
            return "Icecrown"
        else: 
            return self.defaultRealm[message.guild.id]


    async def on_message(self, message):
        #Guard clause statements

        splitSt = message.content.lower().split(" ")
        
        

        if splitSt[0] != await self.getPrefix(message) :
            return
        if message.author.bot == True:
            return
        if message.channel.id != message.channel.id:
            return
        
        await Commands.commandcontroller.handleReply(self, splitSt, message)

        print(f'Message from {message.author}: {message.content}')



class Database:

    def __init__(self) -> None:
        print(pathlib.Path(__file__))
        self.con = sqlite3.connect(str(pathlib.Path(__file__).parent) + ".\discordbot.db")
        self.cur = self.con.cursor()

    def query(self, q):
        return self.cur.execute(q)

    def commit(self):
        return self.con.commit()
    
    def querycommit(self, q):
        self.query(q)
        self.commit()
    
setup()