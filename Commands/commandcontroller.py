import discord
import requests
from bs4 import BeautifulSoup
import math
import re

itemNames = ["Head", "Neck", "Shoulders", "Cloak", "Chest", "Shirt", "Tabard",
              "Bracer", "Gloves", "Belt", "Legs", "Boots", "Ring #1", "Ring #2",
                "Trinket #1", "Trinket #2", "Main-hand", "Off-hand", "Ranged"]



async def handleReply(bot,splitmsg, msg): 
        try:
            match splitmsg[1]:
                case "setprefix":
                        try:
                            splitmsg[2]
                            await handleSetprefix(bot,splitmsg,msg)
                        except IndexError:
                            await msg.reply( "ERROR! Please supply a new prefix with setprefix command!")
                case "defaultrealm":
                        try:
                            splitmsg[2]
                            await handleSetrealm(bot,splitmsg,msg)
                        except IndexError:
                            await msg.reply( "ERROR! Please supply a new prefix with setdefaultrealm command!")
                case "summary":
                        try:
                            splitmsg[2] = splitmsg[2].capitalize()
                            await handleSummary(bot,splitmsg,msg)
                        except IndexError:
                            await msg.reply( "ERROR! Please supply a character name and optionally a realm with summary command!")
                case "info" | "help":
                    await handleInfo(bot,msg)
                case _:
                    await msg.reply( "Unknown command! Please type {prefix} info or {prefix} help".format(prefix = await bot.getPrefix(msg)))
        except IndexError:
            await msg.reply( "Type {prefix} info or {prefix} help to see the list of available commands!".format(prefix = await bot.getPrefix(msg)))

async def handleSetprefix(bot, splitmsg, msg):
    if msg.guild == None:
        await msg.reply( "You can't set a new prefix in private messages!")
        return

    bot.db.query("UPDATE guild SET prefix = '{newPrefix}' WHERE guild_snowflake = {guild};"
                .format(newPrefix = splitmsg[2], guild = msg.guild.id))
    bot.db.commit()

    bot.prefixes[msg.guild.id] = splitmsg[2]

    await msg.reply( "New prefix set successfully!")

async def handleSetrealm(bot, splitmsg, msg):
    if msg.guild == None:
        await msg.reply( "You can't set a default realm in private messages!")
        return
    bot.db.querycommit("UPDATE guild SET realm = '{newPrefix}' WHERE guild_snowflake = {guild};"
                .format(newPrefix = str(splitmsg[2]).capitalize(), guild = msg.guild.id))

    bot.defaultRealm[msg.guild.id] = str(splitmsg[2]).capitalize()

    await msg.reply( "Your default realm is now {newdefault}".format(newdefault = str(splitmsg[2]).capitalize()))

async def handleInfo(bot,msg):
    prefix = await bot.getPrefix(msg)
    rply = discord.Embed(title="List of available commands", description="", color=discord.Colour.dark_green())
    rply.add_field(name="{prefix} info".format(prefix=prefix), value="Lists all the available commands.", inline=False)
    rply.add_field(name="{prefix} summary <name> <realm>".format(prefix=prefix), value="Gives a fairly comprehensive overview of a character, default realm is Icecrown", inline=False)
    rply.add_field(name="{prefix} setprefix".format(prefix=prefix), value="Allows you to set a new prefix for your server", inline=False)
    rply.add_field(name="{prefix} defaultrealm".format(prefix=prefix), value="Allows you to set a new ddefault realm for your server ", inline=False)
    rply.set_footer(text="Hi! This is bot created by Edgy on Icecrown. You can message me at https://discord.gg/cDMptY6yp2")
    await msg.reply(embed=rply)

async def handleSummary(bot,splitmsg, msg): #We should handle DM's!
    
    try:
        realm = splitmsg[3].capitalize()
        data = await getWarmaneData(splitmsg[2], realm)
        talents = await getTalentData(splitmsg[2], realm)
    except IndexError:
        realm = await bot.getDefaultRealm(msg)
        data = await getWarmaneData(splitmsg[2], realm)
        talents = await getTalentData(splitmsg[2], realm)


    items = getGearData(data)


    rply = discord.Embed(title="Character summary for {char}-{realm}".format(char = splitmsg[2].capitalize(), realm = realm)
                         , description="", color=discord.Colour.dark_green())

    rply.add_field(name="Level, Race, Class", value=await getLevelRace(data), inline=True)
    rply.add_field(name="Guild", value=await getGuild(data), inline=True)
    rply.add_field(name='\u200b', value='\u200b', inline=True)

    rply.add_field(name="Specializations", value=await getSpec(data), inline=True)
    rply.add_field(name="Professions", value=await getProfessions(data), inline=True)
    rply.add_field(name='\u200b', value='\u200b', inline=True)

    rply.add_field(name="GearScore", value=str(await calcGS(bot, items)), inline=True)
    rply.add_field(name="Achievement points", value=await getAchivpts(data), inline=True)
    rply.add_field(name='\u200b', value='\u200b', inline=True)

    hk = await getHK(data)
    rply.add_field(name="Honorable kills: Total", value=hk[0], inline=True)
    rply.add_field(name="Honorable kills: Today", value=hk[1], inline=True)
    rply.add_field(name='\u200b', value='\u200b', inline=True)


    rply.add_field(name="Enchants", value=await getEnchants(bot, items, data), inline=True)
    rply.add_field(name="Gems", value=await getGems(bot,items, data), inline=True)
    rply.add_field(name='\u200b', value='\u200b', inline=True)

    rply.set_footer(text="Lidar, when rol marrow?")

    await createGlyphFields(rply, await getMajorGlyphs(talents), await getMinorGlyphs(talents))

    await msg.reply(embed=rply)





async def getWarmaneData(character, realm):
    gear = "https://armory.warmane.com/character/{character}/{realm}/profile".format(character = character, realm = realm)
    response = requests.get(gear, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
    return response

async def getTalentData(character, realm):
    gear = "https://armory.warmane.com/character/{character}/{realm}/talents".format(character = character, realm = realm)

    response = requests.get(gear, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
    return response

async def calcGS(bot, data):
    gs = 0
    weapons = []
    for i, item in enumerate(data):
        try:
            dbItem = bot.items[item[itemNames[i]]['item']]
            if dbItem['class'] == 2 and (dbItem['subclass'] == 1 or dbItem['subclass'] == 5 or dbItem['subclass'] == 8 ):
                weapons.append(dbItem)
            else:
                gs = gs + int(dbItem['gs'])
        except KeyError:
            pass
        
        if len(weapons) == 2:
            gs = gs + math.floor(( int(weapons[0]['gs'])+ int(weapons[0]['gs']))/2 )
        elif len(weapons) == 1:
            gs = gs + weapons[0]['gs']

    return gs

async def getLevelRace(data):
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

async def getGuild(data):
    try:
        soup = BeautifulSoup(data.content, 'html.parser')
        element = soup.select(".guild-name")
        result = BeautifulSoup(str(element[0]), 'html.parser').get_text()
        return result
    except:
        return "None"

async def getProfessions(data):
    try:
        soup = BeautifulSoup(data.content, 'html.parser')
        element = soup.select(".profskills")
        skills = BeautifulSoup(str(element[0]), 'html.parser')
        name = skills.select(".stub")
        result = ""
        for item in name:
            a = BeautifulSoup(str(item), 'html.parser')
            skillName = a.get_text()
            skillName = skillName.replace("\n", "")

            result = result + skillName + "\n"

        return result
    except:
        return "None"

async def getAchivpts(data):
    try:
        soup = BeautifulSoup(data.content, 'html.parser')
        element = soup.select(".achievement-points")
        el  = str(BeautifulSoup(str(element), 'html.parser').get_text())

        el = el.replace("[", "")
        el = el.replace("]", "")
        return el
    except:
        return "None"

async def getHK(data):
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

async def getArena(type, data):
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

async def getSpec(data):
    try:
        soup = BeautifulSoup(data.content, 'html.parser')
        element = soup.select(".specialization")
        skills = BeautifulSoup(str(element[0]), 'html.parser')
        name = skills.select(".text")
        result = ""
        for i, item in enumerate(name):
            a = BeautifulSoup(str(item), 'html.parser')
            skillName = a.get_text()
            skillName = skillName.replace("\n", "")

            result = result + "[" + str(i+1) + "]" + skillName + "\n"

        return result
    except:
        return "None"

async def getMajorGlyphs(data):
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

async def getMinorGlyphs(data):
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

async def getEnchants(bot, data, prof):
    professions = await getProfessions(prof)
    cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))

    class_ = ""
    class_  = await getLevelRace(prof)
    class_ = class_.replace("\n", "")
    class_ = class_.strip()
    class_ = class_.split(" ")
    class_ = class_[2]

    bannedItems = [1, 5, 6, 9, 14, 15]
    missingEnchants = []
    result = ""
    for i, item in enumerate(data):
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
        missingEnchants.remove("Ranged")

    if class_ in ["Priest","Mage","Warlock"]:
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

async def getGems(bot, data, prof):
    
    professions = await getProfessions(prof)
    cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))

    class_ = ""
    class_  = await getLevelRace(prof)
    class_ = class_.replace("\n", "")
    class_ = class_.strip()
    class_ = class_.split(" ")
    class_ = class_[2]


    missingGems = []
    result = ""
    for i, item in enumerate(data):
        bannedItems = [1, 5, 6, 14, 15]
        if i in bannedItems:
            pass
        else:
            try:
                gemAmountFromDB = int(bot.items[item[itemNames[i]]['item']]['gems'])
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
    
async def createGlyphFields(rply, major, minor):
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


        rply.add_field(name="[1] Major Glyphs", value=major[0], inline=True)
        rply.add_field(name="[2] Major Glyphs", value=major[1], inline=True)
        rply.add_field(name='\u200b', value='\u200b', inline=True)

        rply.add_field(name="[1] Minor Glyphs", value=minor[0], inline=True)
        rply.add_field(name="[2] Minor Glyphs", value=minor[1], inline=True)
        rply.add_field(name='\u200b', value='\u200b', inline=True)

def getGearData(data):
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
