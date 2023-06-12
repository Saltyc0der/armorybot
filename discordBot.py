import discord
from discord.ext import commands
import sqlite3
import pathlib
import vars


botSettings = vars.getSettings()

def getBotPrefix(bot, message) -> bool:
    if message.guild == None:
        return ".bot "
    else: 
        return bot.prefixes[message.guild.id]

class ArmoryBot(commands.Bot):

    def __init__(self, *, intents, **options) -> None:
        super().__init__(intents=intents, **options)
        
        self.items = {}
        self.db = sqlite3.connect(str(pathlib.Path(__file__).parent.resolve()) + "/discordbot.db")
        self.cur = self.db.cursor()
        self.prefixes = {}
        self.defaultRealm = {}
        #Don't need to load roles etc. into memory, because those will be rarely hit.

        response = self.cur.execute("SELECT guild_snowflake, prefix, realm FROM guild")
        for prefix in response:
            self.prefixes[prefix[0]] = prefix[1]
            self.defaultRealm[prefix[0]] = prefix[2]

        items = self.cur.execute("SELECT GearScore, ItemLevel, class, gems, ItemID, name, quality, requires, subclass, type FROM items")
        for item in items:
            self.items[item[4]] = {
                                    "gs" : item[0],
                                   "ilvl" : item[1],
                                   "class" : item[2],
                                   "gems" : item[3],
                                   "name" : item[5],
                                   "quality" : item[6],
                                   "requires" : item[7],
                                   "subclass" : item[8],
                                   "type" : item[9]
                                   }
        
    def addPrefix(self, newprefix, guildID):
        self.prefixes[guildID] = newprefix


intents = discord.Intents.default()
intents.message_content = True

bot = ArmoryBot(case_insensitive=True, command_prefix=getBotPrefix, intents=intents)

@bot.event
async def on_ready():
    
    await bot.get_channel(1099702530667204699).send("Hi! I restarted.")
    await bot.get_channel(1099702530667204699).send("I'm currently part of " + str(len(bot.prefixes)) + " guilds.")
    await bot.load_extension("Commands.Commands")
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CheckFailure): # checking which type of error it is
        await ctx.reply(embed=discord.Embed(title="Error!", description="You do not have permission to use this command! \n Only server owners can use this command!", color=discord.Colour.red()))
    if isinstance(error, discord.ext.commands.errors.NoPrivateMessage): # checking which type of error it is
        await ctx.reply(embed=discord.Embed(title="Error!", description="You can't use this command in private messages!", color=discord.Colour.red()))
    if isinstance(error, discord.ext.commands.errors.CommandNotFound): # checking which type of error it is
        await ctx.reply(embed=discord.Embed(title="Error!", description="Command not found! Make sure you typed in the correct command!", color=discord.Colour.red()))

    channel = bot.get_channel(1099702530667204699)
    message = ctx.message.content
    author = ctx.author.name
    if ctx.guild == None: #Error happened in priv msg
        msg = "CONTENT:" + message + "\nERROR: " + str(error)
    else:
        msg = "CONTENT:" + message + "\nERROR: " + str(error)
    await channel.send(msg)

@bot.event
async def on_guild_join(guild):
    await bot.get_channel(1099702530667204699).send("Hi! I just joined: " + guild.name)
    bot.cur.execute("INSERT INTO guild (guild_snowflake, realm, prefix) VALUES ({snowflake}, '{realm}', '{prefix}')"
                    .format(snowflake = guild.id, realm = "Icecrown", prefix = ".bot "))
    bot.db.commit()
    bot.prefixes[guild.id] = ".bot "
    bot.defaultRealm[guild.id] = "Icecrown"


@bot.event
async def on_guild_remove(guild):
    bot.cur.execute("DELETE FROM guild WHERE guild_snowflake = {snowflake}"
                    .format(snowflake = guild.id))
    bot.db.commit()

    await bot.get_channel(1099702530667204699).send("Hi! I just left: " + guild.name)



bot.run(botSettings["token"])



