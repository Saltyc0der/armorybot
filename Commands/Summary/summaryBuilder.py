import discord
import requests
from bs4 import BeautifulSoup
import math
import re


itemNames = ["Head", "Neck", "Shoulders", "Cloak", "Chest", "Shirt", "Tabard",
              "Bracer", "Gloves", "Belt", "Legs", "Boots", "Ring #1", "Ring #2",
                "Trinket #1", "Trinket #2", "Main-hand", "Off-hand", "Ranged"]

class SummaryBuilder:

    def __init__(self, name, realm, bot):
        self.character = Character(name, realm, bot)

    async def Result(self) -> discord.Embed:
        if self.character.name == None:
            emb = discord.Embed(title="Error - No character name!", description="Please enter character name! \nUsage of the command: summary <character name> [realm name]", color=discord.Colour.red())
            return emb
        else:
            return await self.buildEmbed()

    async def buildEmbed(self):
        if self.character.error:
            emb = discord.Embed(title="Error - Character not found!", description="Character name not found!", color=discord.Colour.red())
        else:
                emb = discord.Embed(title="Character summary for {char}-{realm}".format(char = self.character.name.capitalize(), realm = self.character.realm)
                         , description="", color=discord.Colour.dark_green())

                emb.add_field(name="Level, Race, Class", value=self.character.level, inline=True)
                emb.add_field(name="Guild", value=self.character.guild, inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="Specializations", value=self.character.spec, inline=True)
                emb.add_field(name="Professions", value=self.character.professions, inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="GearScore", value=str(self.character.GS), inline=True)
                emb.add_field(name="Achievement points", value=self.character.Achivpts, inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)


                emb.add_field(name="Honorable kills: Total", value=self.character.HK[0], inline=True)
                emb.add_field(name="Honorable kills: Today", value=self.character.HK[1], inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="Enchants", value=self.character.enchants, inline=True)
                emb.add_field(name="Gems", value=self.character.gems, inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="[1] Major Glyphs", value=self.character.majorGlyphs[0], inline=True)
                emb.add_field(name="[2] Major Glyphs", value=self.character.majorGlyphs[1], inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.add_field(name="[1] Minor Glyphs", value=self.character.minorGlyphs[0], inline=True)
                emb.add_field(name="[2] Minor Glyphs", value=self.character.minorGlyphs[1], inline=True)
                emb.add_field(name='\u200b', value='\u200b', inline=True)

                emb.set_footer(text="Lidar, when rol marrow?")
        return emb

class Character:
    def __init__(self, name, realm, bot):
        self.bot = bot
        self.name = name
        self.realm = realm
        
        self.error = False

        self.GS = 0
        self.level = ""
        self.guild = ""
        self.professions = ""
        self.Achivpts = ""
        self.HK = ""
        self.spec = ""
        self.majorGlyphs = ""
        self.minorGlyphs = ""
        self.gems = ""
        self.enchants = ""

        self.buildCharacter()

    def buildCharacter(self):
        profile = self.getProfileData()
        soup = BeautifulSoup(profile.content, "html.parser")
        #check 
        if bool(soup.find(text="Page not found")):
            self.error = True
            return 
        talent = self.getTalentData()
        items = self.getItemsFromProfile(profile)

        self.GS = self.calcGS(items)
        self.level = self.getLevelRace(profile)
        self.guild = self.getGuild(profile)
        self.professions = self.getProfessions(profile)
        self.Achivpts = self.getAchivpts(profile)
        self.HK = self.getHK(profile)
        self.spec = self.getSpec(profile)
        self.majorGlyphs = self.getMajorGlyphs(talent)
        self.minorGlyphs = self.getMinorGlyphs(talent)
        self.gems = self.getGems(items)
        self.enchants = self.getEnchants(items)

    def getProfileData(self):
        gear = "https://armory.warmane.com/character/{character}/{realm}/profile".format(character = self.name, realm = self.realm)
        response = requests.get(gear, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
        return response

    def getTalentData(self):
        gear = "https://armory.warmane.com/character/{character}/{realm}/talents".format(character = self.name, realm = self.realm)
        response = requests.get(gear, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
        return response

    def calcGS(self, items):
        gs = 0
        weapons = []
        for i, item in enumerate(items):
            try:
                dbItem = self.bot.items[item[itemNames[i]]['item']]
                subclass = int(dbItem['subclass'])
                if int(dbItem['class']) == 2 and (subclass == 1 or subclass == 5 or subclass == 8 ):
                    weapons.append(dbItem)
                else:
                    gs = gs + int(dbItem['gs'])
            except KeyError:
                pass
        
        if len(weapons) == 2:
            gs = gs + math.floor(( int(weapons[0]['gs'])+ int(weapons[1]['gs']))/2 )
        elif len(weapons) == 1:
            gs = gs + int(weapons[0]['gs'])
        return gs

    def getLevelRace(self,data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".level-race-class")
            el  = str(BeautifulSoup(str(element), 'html.parser').get_text())
            el = el.replace("Level", "")
            result = el.split(",", 1)[0]
            result = result.replace("[", "")
            return result
        except:
            return "None"

    def getGuild(self,data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".guild-name")
            result = BeautifulSoup(str(element[0]), 'html.parser').get_text()
            return result
        except:
            return "None"

    def getProfessions(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".profskills")
            skills = BeautifulSoup(str(element[0]), 'html.parser')
            name = skills.select(".stub")
            result = ""
            for item in name:
                a = BeautifulSoup(str(item), 'html.parser')
                skillName = a.get_text()
                splitStr = skillName.split()
                
                for i, str_ in enumerate(splitStr):
                    if i == 1:
                        result = result + " " + str_
                    else:
                        result = result + str_
                result = result + "\n"

            return result
        except:
            return "None"

    def getAchivpts(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".achievement-points")
            el  = str(BeautifulSoup(str(element), 'html.parser').get_text())
            el = el.replace("[", "")
            el = el.replace("]", "")
            return el
        except:
            return "None"

    def getHK(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".pvpbasic")
            skills = BeautifulSoup(str(element[0]), 'html.parser')
            name = skills.select(".stub")
            result = []
            for item in name:
                b = ""
                a = ""
                a = BeautifulSoup(str(item), 'html.parser')
                b = a.select(".value")
                b = str(b[0])
                #im lazy
                b = b.replace('<span class="value">', '')
                b = b.replace('</span>', '')

                result.append(str(b))

            return result
        except:
            return ["None", "None"]

    def getSpec(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".specialization")
            skills = BeautifulSoup(str(element[0]), 'html.parser')
            name = skills.select(".text")
            result = ""
            skill = ""
            for i, item in enumerate(name):
                a = BeautifulSoup(str(item), 'html.parser')
                skillName = a.get_text()
                splitStr = skillName.split()
                for x, str_ in enumerate(splitStr):
                    if x == 1:
                        skill = skill + " " + str_
                    else:
                        skill = skill + str_
                result = result + "[" + str(i+1) + "] " + skill + "\n"
                skill = ""
            return result
        except:
            return "None"

    def getMajorGlyphs(self, data):
        soup = BeautifulSoup(data.content, 'html.parser')
        element = soup.select("div[data-glyphs]")
        result = ["","","",""]
        for i, glyphset in enumerate(element):
            a = BeautifulSoup(str(glyphset), 'html.parser')
            b = a.select(".glyph.major")
            for glyph in b:
                x = BeautifulSoup(str(glyph), 'html.parser').get_text()
                x = x.replace("\n", "")
                result[i] = result[i] + x + "\n"
        return result

    def getMinorGlyphs(self, data):
        soup = BeautifulSoup(data.content, 'html.parser')
        element = soup.select("div[data-glyphs]")
        result = ["","","",""]
        for i, glyphset in enumerate(element):
            a = BeautifulSoup(str(glyphset), 'html.parser')
            b = a.select(".glyph.minor")
            for glyph in b:
                x = BeautifulSoup(str(glyph), 'html.parser').get_text()
                x = x.replace("\n", "")
                result[i] = result[i] + x + "\n"

        return result

    #NEEDS REWRITE BAD!
    def getEnchants(self, items):
        professions = self.professions
        cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))

        class_ = self.level
        class_ = class_.replace("\n", "")
        class_ = class_.strip()
        class_ = class_.split(" ")
        class_ = class_[2]

        bannedItems = [1, 5, 6, 9, 14, 15]
        missingEnchants = []
        result = ""
        for i, item in enumerate(items):
            if i in bannedItems:
                pass
            else:
                try:
                    item[itemNames[i]]['item'] #checking if item exists
                    try:
                        item[itemNames[i]]['ench']
                    except KeyError:
                            missingEnchants.append(itemNames[i])
                except KeyError:
                    pass #item didn't exist, do nothing.
        if "Enchanting" in cleanprofessions:
            pass
        else:
            try:
                missingEnchants.remove("Ring #1")
                missingEnchants.remove("Ring #2")
            except ValueError:
                pass
        if class_ != "Hunter":
            try:
                missingEnchants.remove("Ranged")
            except ValueError:
                pass
        if class_ in ["Priest","Mage","Warlock", "Druid"]:
            try:
                missingEnchants.remove("Off-hand")
            except ValueError:
                pass
        if len(missingEnchants) != 0:
            result = "Missing enchants from: "
            for item in missingEnchants:
                result = result + item + ","
            result = result[:-1]
            return result
        else:
            return "All items are enchanted!"

    def getGems(self, items):
    
        professions = self.professions
        cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))
        class_  = self.level
        class_ = class_.replace("\n", "")
        class_ = class_.strip()
        class_ = class_.split(" ")
        class_ = class_[2]


        missingGems = []
        result = ""
        for i, item in enumerate(items):
            bannedItems = [1, 5, 6, 14, 15]
            if i in bannedItems:
                pass
            else:
                try:
                    gemAmountFromDB = int(self.bot.items[item[itemNames[i]]['item']]['gems'])
                    if gemAmountFromDB == 0:
                        pass
                    else:
                        try:
                            if i == 9:
                                gemAmountFromDB = gemAmountFromDB + 1
                            if "Blacksmithing" in cleanprofessions:
                                if i == 7 or i == 8:
                                    gemAmountFromDB = gemAmountFromDB + 1

                            itemGemAmount = len(item[itemNames[i]]['gems'])
                            if gemAmountFromDB != int(itemGemAmount):
                                missingGems.append(itemNames[i])
                        except KeyError:
                            missingGems.append(itemNames[i])
                except KeyError:
                    pass
                    
        if class_ in ["Shaman", "Paladin", "Druid"]:
            try:
                missingGems.remove("Ranged")
            except:
                pass

        if len(missingGems) != 0:

            result = "Missing gems from: "
            for item in missingGems:
                result = result + str(item) + ","

            result = result[:-1]
            return result
        else:
            return "All items are gemmed!"

    def createGlyphFields(emb, major, minor):
        try:
            major[0]
        except:
            major[0] - "None"
        try:
            major[1]
        except:
            major[1] - "None"

        try:
            minor[0]
        except:
            minor[0] - "None"
        try:
            minor[1]
        except:
            minor[1] - "None"


        emb.add_field(name="[1] Major Glyphs", value=major[0], inline=True)
        emb.add_field(name="[2] Major Glyphs", value=major[1], inline=True)
        emb.add_field(name='\u200b', value='\u200b', inline=True)

        emb.add_field(name="[1] Minor Glyphs", value=minor[0], inline=True)
        emb.add_field(name="[2] Minor Glyphs", value=minor[1], inline=True)
        emb.add_field(name='\u200b', value='\u200b', inline=True)

    def getItemsFromProfile(self, data):
        soup = BeautifulSoup(data.content, 'html.parser')
        itemlinks = soup.select(".icon-quality")
        items = []

        for i,item in enumerate(itemlinks):
            split = [] #CAN SOMEONE EXPLAIN TO ME, WHY DATA FROM PREVIOUS LOOP IS CARRIED OVER?
            a = None    #HOLY FUCK, WHAT IS WRONG WITH THIS LANGUAGE
            b = None
            a = BeautifulSoup(str(item), 'html.parser')
            b = a.find("a").get("rel")

            item = {}
            if b == None:
                item[itemNames[i]] = {}
            else:
                split = b[0].split("&")


            try:#easiest way to do. I know it looks horrible. I'm crying too.
                item[itemNames[i]]  =  {
                    "item" : split[0].replace("item=", ""),
                    }
                if split[1].startswith("ench") :#only 1 ench id
                    item[itemNames[i]]  =  {
                        "item" : split[0].replace("item=", ""),
                        "ench" : split[1].replace("ench=", "")
                        }
                if split[1].startswith("gem")  :#only 1 ench id
                    item[itemNames[i]]  =  {
                        "item" : split[0].replace("item=", ""),
                        "gems" : [i for i in split[1].replace("gems=", "").split(":") if i != "0" ]
                        }
            except IndexError:
                pass

            try:
                if split[2].startswith("gem"):
                    item[itemNames[i]]  =  {
                        "item" : split[0].replace("item=", ""),
                        "ench" : split[1].replace("ench=", ""),
                        "gems" : [i for i in split[2].replace("gems=", "").split(":") if i != "0"]
                        }
            except IndexError:
                pass

            items.append(item)

        return items