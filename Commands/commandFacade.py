import discord
from discord.ext import commands
import Commands.Summary.summaryBuilder as Summary
import Commands.SetPrefix.setPrefixBuilder as SetPrefix
import Commands.SetDefaultRealm.setDefaultRealmBuilder as SetDefaultRealm
import Commands.Help.helpBuilder as Help

rBot = None #ref to bot

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
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
async def setprefix(ctx, prefix=None):
    await ctx.reply(embed=await SetPrefix.SetPrefixBuilder(prefix,ctx.guild.id, rBot).Result())

@commands.command()
async def summary(ctx, character=None, realm=None):
    if realm == None:
        realm = getDefaultRealm(ctx)
    await ctx.reply(embed=await Summary.SummaryBuilder(character, realm, rBot).Result())

@commands.command(aliases=['info'])
async def help(ctx):
    await ctx.reply(embed=await Help.HelpBuilder(getPrefix(ctx),getDefaultRealm(ctx)).Result())

@commands.guild_only()
@is_guild_owner()
@commands.command(aliases=['setrealm'])
async def setdefaultrealm(ctx, realm=None):
   await ctx.reply(embed=await SetDefaultRealm.SetDefaultRealmBuilder(realm,ctx.guild.id, rBot).Result())



async def setup(bot):
    bot.remove_command("help")
    bot.add_command(setprefix)
    bot.add_command(summary)
    bot.add_command(help)
    bot.add_command(setdefaultrealm)
    setBotRef(bot)


