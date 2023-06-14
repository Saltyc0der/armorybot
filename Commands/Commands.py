import discord
from discord.ext import commands
from Commands.Character import Character
from Commands.Summary import Summary
from Commands.SetPrefix import SetPrefix
from Commands.SetDefaultRealm import SetDefaultRealm
from Commands.Help import Help
from Commands.Achiv import Achiv
from Commands.IcecrownAchiv import IcecrownAchiv

from Commands.NaxxAchiv import NaxxAchiv
from Commands.RSAchiv import RSAchiv
from Commands.TocAchiv import TocAchiv
from Commands.UlduarAchiv import UldAchiv

rBot = None 

def is_guild_owner():
    def predicate(ctx):
        return (ctx.guild is not None and ctx.guild.owner_id == ctx.author.id) or (ctx.guild is not None and ctx.author.server_premission.administrator)
    return commands.check(predicate)

def setBotRef(bot): #set bot ref
    global rBot
    rBot = bot

def getPrefix(ctx):
        if ctx.guild == None:
            return ".bot "
        else:
            return rBot.prefixes[ctx.guild.id]
          #how do i get bot here.

def getDefaultRealm(ctx):
    if ctx.guild == None:
        return "Icecrown"
    else:
        return rBot.defaultRealm[ctx.guild.id]
          #how do i get bot here.
    
@commands.guild_only()
@is_guild_owner()
@commands.command()
async def setprefix(ctx, prefix=None, space=None):
    await ctx.reply(embed=await SetPrefix(prefix,space, ctx.guild.id, rBot).Result())

@commands.command(aliases=['inspect', 'stalk'])
async def summary(ctx, character=None, realm=None):
        emb = discord.Embed(title="Command is running, be patient!", 
                        description="Beep Boop stuff is happening", 
                        color=discord.Colour.yellow())
        msg = await ctx.reply(embed=emb)
        if realm == None:
            realm = getDefaultRealm(ctx)
        await msg.edit(embed=await Summary(Character(character, realm,"", rBot)).Result())

@commands.command()
async def achiv(ctx, character=None, realm=None):
    emb = discord.Embed(title="Command is running, be patient!", 
                    description="How's your day been?", 
                    color=discord.Colour.yellow())
    msg = await ctx.reply(embed=emb)
    if realm == None:
        realm = getDefaultRealm(ctx)
    await msg.edit(embed=await Achiv(Character(character, realm,"", rBot)).Result())


@commands.command()
async def icc(ctx, character=None, realm=None):
    emb = discord.Embed(title="Command is running, be patient!", 
                    description="How's your day been?", 
                    color=discord.Colour.yellow())
    msg = await ctx.reply(embed=emb)
    if realm == None:
        realm = getDefaultRealm(ctx)
    await msg.edit(embed=await IcecrownAchiv(Character(character, realm,"", rBot)).Result())

@commands.command(aliases=['ruby', 'rubysanctum'])
async def rs(ctx, character=None, realm=None):
    emb = discord.Embed(title="Command is running, be patient!", 
                    description="How's your day been?", 
                    color=discord.Colour.yellow())
    msg = await ctx.reply(embed=emb)
    if realm == None:
        realm = getDefaultRealm(ctx)
    await msg.edit(embed=await RSAchiv(Character(character, realm,"", rBot)).Result())

@commands.command(aliases=['uld'])
async def ulduar(ctx, character=None, realm=None):
    emb = discord.Embed(title="Command is running, be patient!", 
                    description="How's your day been?", 
                    color=discord.Colour.yellow())
    msg = await ctx.reply(embed=emb)
    if realm == None:
        realm = getDefaultRealm(ctx)
    await msg.edit(embed=await UldAchiv(Character(character, realm,"", rBot)).Result())

@commands.command(aliases=['naxxaramas', 'nax', "naxxramas"])
async def naxx(ctx, character=None, realm=None):
    emb = discord.Embed(title="Command is running, be patient!", 
                    description="How's your day been?", 
                    color=discord.Colour.yellow())
    msg = await ctx.reply(embed=emb)
    if realm == None:
        realm = getDefaultRealm(ctx)
    await msg.edit(embed=await NaxxAchiv(Character(character, realm,"", rBot)).Result())

@commands.command(aliases=['togc', 'trial'])
async def toc(ctx, character=None, realm=None):
    emb = discord.Embed(title="Command is running, be patient!", 
                    description="How's your day been?", 
                    color=discord.Colour.yellow())
    msg = await ctx.reply(embed=emb)
    if realm == None:
        realm = getDefaultRealm(ctx)
    await msg.edit(embed=await TocAchiv(Character(character, realm,"", rBot)).Result())

@commands.command(aliases=['info'])
async def help(ctx):
    await ctx.reply(embed=await Help(getPrefix(ctx),getDefaultRealm(ctx)).Result())

@commands.guild_only()
@is_guild_owner()
@commands.command(aliases=['setrealm'])
async def setdefaultrealm(ctx, realm=None):
   await ctx.reply(embed=await SetDefaultRealm(realm,ctx.guild.id, rBot).Result())



async def setup(bot):
    bot.remove_command("help")
    bot.add_command(help)
    bot.add_command(icc)
    bot.add_command(rs)
    bot.add_command(naxx)
    bot.add_command(ulduar)
    bot.add_command(toc)
    bot.add_command(setprefix)
    bot.add_command(summary)
    bot.add_command(achiv)
    bot.add_command(setdefaultrealm)
    setBotRef(bot)


