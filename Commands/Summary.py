import discord

class Summary:

    def __init__(self, character):
        self.character = character

    async def Result(self) -> discord.Embed:
        if self.character.name == None:
            emb = discord.Embed(title="Error - No character name!", description="Please enter character name! \nUsage of the command: summary <character name> [realm name]", color=discord.Colour.red())
            return emb
        else:
            return await self.buildEmbed()

    async def buildEmbed(self):
        if self.character.error:
            emb = discord.Embed(title="Error - Character not found!", 
                                description="Character name not found!", 
                                color=discord.Colour.red())
        else:
                emb = discord.Embed(title="Character summary for {char}-{realm}".format(char = self.character.name.capitalize(), realm = self.character.realm)
                         , description="", color=discord.Colour.dark_green())

                emb.add_field(name="Level, Race, Class", value=self.character.getLevelRace(), inline=True)
                emb.add_field(name="Guild", value=self.character.getGuild(), inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="Specializations", value=self.character.getSpec(), inline=True)
                emb.add_field(name="Professions", value=self.character.getProfessions(), inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="GearScore", value=str(self.character.getGS()), inline=True)
                emb.add_field(name="Achievement points", value=self.character.getAchivPts(), inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="Enchants", value=self.character.getEnchants(), inline=True)
                emb.add_field(name="Gems", value=self.character.getGems(), inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                majorGlyphs = self.character.getGlyphs("major")
                minorGlyphs = self.character.getGlyphs("minor")

                emb.add_field(name="[1] Major Glyphs", value=majorGlyphs[0], inline=True)
                emb.add_field(name="[2] Major Glyphs", value=majorGlyphs[1], inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="[1] Minor Glyphs", value=minorGlyphs[0], inline=True)
                emb.add_field(name="[2] Minor Glyphs", value=minorGlyphs[1], inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)




                emb.set_footer(text="Lidar, when rol marrow?")
        return emb