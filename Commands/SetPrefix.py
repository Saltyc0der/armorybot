import discord

class SetPrefix:
        
        def __init__(self, newPrefix,space, snowflake, bot) -> None:
            self.prefix = newPrefix
            self.space = space
            self.bot = bot
            self.snowflake = snowflake

        async def Result(self):
            if self.prefix == None:
                return discord.Embed(title="No new prefix supplied!",
                                     description="Please enter new prefix you would like to use! \nUsage of the command: setprefix <new prefix>",
                                       color=discord.Colour.red())
            else:
                if self.space.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'nospace']:
                    self.prefix = self.prefix
                else:
                    self.prefix = self.prefix + " "

                self.bot.db.querycommit("UPDATE guild SET prefix = '{newPrefix}' WHERE guild_snowflake = {guild};"
                            .format(newPrefix = self.prefix, guild = self.snowflake))
                self.bot.addPrefix(self.prefix, self.snowflake)
                return discord.Embed(title="New prefix successfully set!",
                                     description="You have set your bot's prefix to {newPrefix}".format(newPrefix = self.prefix),
                                       color=discord.Colour.green())
