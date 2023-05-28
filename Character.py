import math
import requests
import re
from bs4 import BeautifulSoup
import json

itemNames = ["Head", "Neck", "Shoulders", "Cloak", "Chest", "Shirt", "Tabard",
              "Bracer", "Gloves", "Belt", "Legs", "Boots", "Ring #1", "Ring #2",
              "Trinket #1", "Trinket #2", "Main-hand", "Off-hand", "Ranged"]

class Character:
    def __init__(self, name, realm, server, botContext):
        # Input
        self.bot = botContext
        self.name = name
        self.realm = realm

        self.profileHTML = None
        self.talentHTML = None
        self.apiProfile = None
        self.apiGuild = None
        self.error = False
        self.items = None
        self.achivCache = []


    def check_required_data(data_type):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if self.__check_required_data(data_type):
                    return func(self)
                else:
                    raise ValueError(f"Required {data_type} data is missing")
            return wrapper
        return decorator


    def __check_required_data(self, _type):
        if _type == "profile" and self.profileHTML is None:
            gear = "https://armory.warmane.com/character/{character}/{realm}/profile".format(
                character=self.name, realm=self.realm)
            self.profileHTML = requests.get(gear, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content

        if _type == "talents" and self.talentHTML is None:
            gear = "https://armory.warmane.com/character/{character}/{realm}/talents".format(
                character=self.name, realm=self.realm)
            self.talentHTML = requests.get(gear, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content

        if _type == "apiProfile" and self.apiProfile is None:
            gear = "https://armory.warmane.com/api/character/{character}/{realm}/summary".format(
                character=self.name, realm=self.realm)
            self.apiProfile = requests.get(gear, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content

        if _type == "apiGuild" and self.apiGuild is None:
            gear = "https://armory.warmane.com/api/guild/{guild}/{realm}/summary".format(
                guild=self.name, realm=self.realm)
            self.apiGuild = requests.get(gear, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content
        
        if _type == "items" and self.items is None:
            self.__check_required_data("profile")

            soup = BeautifulSoup(self.profileHTML.text, 'html.parser')
            itemlinks = soup.select(".icon-quality")
            self.items = []

            for item in itemlinks:
                item_data = {}
                rel = item.find("a").get("rel")

                if rel is None:
                    item_data[itemNames[len(self.items)]] = {}
                else:
                    split = rel.split("&")
                    item_data[itemNames[len(self.items)]] = {"item": split[0].replace("item=", "")}

                    if split[1].startswith("ench"):
                        item_data[itemNames[len(self.items)]]["ench"] = split[1].replace("ench=", "")
                    elif split[1].startswith("gem"):
                        item_data[itemNames[len(self.items)]]["gems"] = [i for i in split[1].replace("gems=", "").split(":") if i != "0"]

                    if len(split) >= 3 and split[2].startswith("gem"):
                        item_data[itemNames[len(self.items)]]["gems"] = [i for i in split[2].replace("gems=", "").split(":") if i != "0"]

                self.items.append(item_data)
        return True

    @check_required_data("profile")
    def getGS(self):
        gs = 0
        weapons = []

        for i, item in enumerate(self.items):
            try:
                dbItem = self.bot.items[item[itemNames[i]]['item']]
                subclass = int(dbItem['subclass'])
                if int(dbItem['class']) == 2 and subclass in [1, 5, 8]:
                    weapons.append(dbItem)
                else:
                    gs += int(dbItem['gs'])
            except KeyError:
                pass

        gs += sum(int(weapon['gs']) for weapon in weapons)
        return str(gs)

    @check_required_data("profile")
    def getGuild(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select_one(".guild-name")
            result = element.get_text()
            return result
        except:
            return "None"

    @check_required_data("profile")
    def getProfessions(self):
        try:
            soup = BeautifulSoup(self.profileHTML, 'html.parser')
            element = soup.select_one(".profskills")
            name = element.select(".stub")
            result = ""
            
            for item in name:
                skillName = item.get_text()
                splitStr = skillName.split()
                result += " ".join(splitStr) + "\n"
            
            return result
        except:
            return "None"

    @check_required_data("profile")
    def getAchivPts(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select_one(".achievement-points")
            if element:
                return element.get_text().strip("[]")
            else:
                return "None"
        except:
            return "None"

    @check_required_data("profile")
    def getHK(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select(".pvpbasic")
            name = element[0].select(".stub")
            result = [item.select_one(".value").get_text() for item in name]

            return result
        except:
            return ["None", "None"]

    @check_required_data("profile")
    def getSpec(self, data):
        try:
            soup = BeautifulSoup(data.content, 'html.parser')
            element = soup.select_one(".specialization")
            name = element.select(".text")
            result = ""
            
            for i, item in enumerate(name):
                skillName = item.get_text()
                splitStr = skillName.split()
                skill = " ".join(splitStr[1:])
                result += f"[{i+1}] {skill}\n"
            
            return result
        except:
            return "None"
    
    @check_required_data("profile")
    def getEnchants(self):
        items = self.items 
        professions = self.professions
        cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))

        class_ = self.level.split()[-1].strip()

        bannedItems = {1, 5, 6, 9, 14, 15}
        missingEnchants = []

        for i, item in enumerate(items):
            if i not in bannedItems:
                try:
                    if 'ench' not in item[itemNames[i]]:
                        missingEnchants.append(itemNames[i])
                except KeyError:
                    pass

        if "Enchanting" not in cleanprofessions:
            missingEnchants = [item for item in missingEnchants if item not in ["Ring #1", "Ring #2"]]

        if class_ != "Hunter":
            missingEnchants = [item for item in missingEnchants if item != "Ranged"]

        if class_ in ["Priest", "Mage", "Warlock", "Druid"]:
            missingEnchants = [item for item in missingEnchants if item != "Off-hand"]

        if missingEnchants:
            return "Missing enchants from: " + ", ".join(missingEnchants)
        else:
            return "All items are enchanted!"
    
    @check_required_data("profile")
    def getGems(self):
        items = self.items 
        professions = self.professions
        cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))
        class_ = self.level.split()[2].strip()

        bannedItems = {1, 5, 6, 14, 15}
        missingGems = []

        for i, item in enumerate(items):
            if i not in bannedItems:
                try:
                    gemAmountFromDB = int(self.bot.items[item[itemNames[i]]['item']]['gems'])
                    if gemAmountFromDB != 0:
                        if i == 9:
                            gemAmountFromDB += 1
                        if "Blacksmithing" in cleanprofessions and (i == 7 or i == 8):
                            gemAmountFromDB += 1
                        itemGemAmount = len(item[itemNames[i]]['gems'])
                        if gemAmountFromDB != itemGemAmount:
                            missingGems.append(itemNames[i])
                except KeyError:
                    missingGems.append(itemNames[i])

        if class_ in ["Shaman", "Paladin", "Druid"]:
            missingGems = [item for item in missingGems if item != "Ranged"]

        if missingGems:
            return "Missing gems from: " + ", ".join(missingGems)
        else:
            return "All items are gemmed!"

    @check_required_data("talents")
    def getGlyphs(self, glyphType):
        soup = BeautifulSoup(self.talentHTML, 'html.parser')
        glyphs = soup.select(f"div[data-glyphs] .glyph.{glyphType}")
        result = [""] * 4

        for i, glyph in enumerate(glyphs):
            text = glyph.get_text().replace("\n", "")
            result[i % 4] += text + "\n"

        return result

    @check_required_data("profile")
    def getLevelRace(self):
        try:
            soup = BeautifulSoup(self.profileHTML, 'html.parser')
            element = soup.select_one(".level-race-class")
            result = element.get_text().split(",", 1)[0].replace("Level", "").replace("[", "")
            return result
        except:
            return "None"
    
    def requestAchivCategory(self, achivCategory):
        URL = "https://armory.warmane.com/character/{character}/{realm}/achievements".format(
                character=self.name, realm=self.realm)
        form_data = {
            "category": achivCategory
        }
        res = requests.post(URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'},
                data=form_data).content
        

        content = json.loads(res)
        return content['content']

    def getAchiv(self, instance):
        list_of_instances = {
            "icc10" :15041,
            "icc25" :15042,
            "toc10" : 15001,
            "toc25" : 15002,
            "uld10" : 14961,
            "uld25" : 14962,
            "naxx10" : 14922,
            "naxx25" : 14923
        }
        list_of_achivs = {
            15041 : ["#ach4636", "#ach4532"],
            15042 : ["#ach4584", "#ach4597"],
            15001 : ["#ach3917", "#ach3918"],
            15002 : ["#ach3812", "#ach3916"],
            14961 : [],
            14962 : [],
            14922 : ["#ach4817", "#ach4818"],
            14923 : ["#ach4815", "#ach4816"],
        }
        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        soup = BeautifulSoup(data, 'html.parser')
        for class_name in list_of_achivs[list_of_instances[instance]]:
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    result = result + "✅ " + str(element.select_one(".title").get_text()) + "\n"
                else:
                    result = result + "❌ " + str(element.select_one(".title").get_text()) + "\n"
        return result
