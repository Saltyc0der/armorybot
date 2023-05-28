import discord

class Achiv:

    def __init__(self, character):
        self.character = character

    async def Result(self) -> discord.Embed:
        if self.character.name == None:
            emb = discord.Embed(title="Error - No character name!", description="Please enter character name! \nUsage of the command: summary <character name> [realm name]", color=discord.Colour.red())
            return emb
        else:
            return await self.buildEmbed()

    async def buildEmbed(self):

        emb = discord.Embed(title="Character achievments for {char}-{realm}".format(char = self.character.name.capitalize(), realm = self.character.realm)
                    , description="", color=discord.Colour.dark_green())

        emb.add_field(name="Icecrown Citadel 10", value=self.character.getAchiv("icc10"), inline=True)
        emb.add_field(name="Icecrown Citadel 25", value=self.character.getAchiv("icc25"), inline=True)
        emb.add_field(name='\u200b', value='\u200b', inline=False)

        emb.add_field(name="Trial of the Crusader 10", value=self.character.getAchiv("toc10"), inline=True)
        emb.add_field(name="Trial of the Crusader 25", value=self.character.getAchiv("toc25"), inline=True)
        emb.add_field(name='\u200b', value='\u200b', inline=False)
        
        emb.add_field(name="Ruby Sanctum 10", value=self.character.getAchiv("naxx10"), inline=True)
        emb.add_field(name="Ruby Sanctum 25", value=self.character.getAchiv("naxx25"), inline=True)
        emb.add_field(name='\u200b', value='\u200b', inline=False)

        emb.set_footer(text="Lidar, when rol marrow?")
        
        if self.character.error:
            emb = discord.Embed(title="Error - Character not found!", 
                                description="Character name not found!", 
                                color=discord.Colour.red())

        return emb