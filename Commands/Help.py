import discord

class Help:
        
        def __init__(self, prefix, realm) -> None:
            self.prefix = prefix
            self.realm = realm

        async def Result(self):
            emb = discord.Embed(title="List of available commands", description="", color=discord.Colour.dark_green())
            emb.add_field(name="", value="<> means required argument, [] means optional argument. Bot also responds to DMs")
            emb.add_field(name="{prefix} info | help".format(prefix=self.prefix), value="Lists all the available commands.", inline=False)
            emb.add_field(name="{prefix} summary | stalk <name> [realm]".format(prefix=self.prefix), value="Gives a overview of a character, current default realm for server is {realm}".format(realm = self.realm), inline=False)
            emb.add_field(name="{prefix} achiv | icc | rs | toc | uld | naxx <name> [realm]".format(prefix=self.prefix), value="Give an overview for specified instance achievments, current default realm for server is {realm}".format(realm = self.realm), inline=False)
            emb.add_field(name="{prefix} setprefix <newprefix> [nospace]".format(prefix=self.prefix), value="Allows you to set a new prefix for your server.\n Optional [nospace] parameter (set it to 1 | y | yes | nospace ) allows you to set prefix without space", inline=False)
            emb.add_field(name="{prefix} defaultrealm | setrealm <realm>".format(prefix=self.prefix), value="Allows you to set a new default realm for your server ", inline=False)
            emb.set_footer(text='Hi! Bot made by Edgy on Icecrown. You can message me at "edgy.at.linux" on discord')
            return emb