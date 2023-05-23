import discord

class SetDefaultRealm:
        
        def __init__(self, realm,snowflake, bot) -> None:
            self.realm = realm
            self.bot = bot
            self.snowflake = snowflake

        async def Result(self):
            if self.realm == None:
                return discord.Embed(title="No realm supplied!",
                                     description="Please enter the realm you would like to use as a default realm! \nUsage of the command: setdefaultrealm <realm>",
                                       color=discord.Colour.red())
            else:
                self.realm = self.realm.lower().capitalize()
                self.bot.db.querycommit("UPDATE guild SET realm = '{realm}' WHERE guild_snowflake = {guild};"
                            .format(realm = self.realm, guild = self.snowflake))
                self.bot.prefixes[self.snowflake] = self.realm
                return discord.Embed(title="Updated default realm successfully!",
                                     description="You have set your bot's default realm to {realm}".format(realm = self.realm),
                                       color=discord.Colour.green())
