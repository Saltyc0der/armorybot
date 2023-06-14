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
        self.realm = realm.lower().capitalize()

        self.profileHTML = None
        self.talentHTML = None
        self.apiProfile = None
        self.apiGuild = None
        self.error = False
        self.items = None


    def check_required_data(data_type):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if self.__check_required_data(data_type):
                    return func(self,*args, **kwargs)
                else:
                    raise ValueError(f"Required {data_type} data is missing")
            return wrapper
        return decorator

    def check_error(func):
        def wrapper(self, *args, **kwargs):
            if self.error == False:
                return func(self,*args, **kwargs)
            else:
                pass
        return wrapper

    def __check_required_data(self, _type):
        if _type == "profile" and self.profileHTML is None:
            URL = "https://armory.warmane.com/character/{character}/{realm}/profile".format(
                character=self.name, realm=self.realm)
            self.profileHTML = requests.get(URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content
            soup = BeautifulSoup(self.profileHTML, "html.parser")
            if bool(soup.find(text="Page not found")):
                self.error = True


        if _type == "talents" and self.talentHTML is None:
            URL = "https://armory.warmane.com/character/{character}/{realm}/talents".format(
                character=self.name, realm=self.realm)
            self.talentHTML = requests.get(URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content
            soup = BeautifulSoup(self.talentHTML, "html.parser")
            if bool(soup.find(text="Page not found")):
                self.error = True

        if _type == "apiProfile" and self.apiProfile is None:
            URL = "https://armory.warmane.com/api/character/{character}/{realm}/summary".format(
                character=self.name, realm=self.realm)
            self.apiProfile = requests.get(URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content

        if _type == "apiGuild" and self.apiGuild is None:
            URL = "https://armory.warmane.com/api/guild/{guild}/{realm}/summary".format(
                guild=self.name, realm=self.realm)
            self.apiGuild = requests.get(URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}).content
        
        if _type == "items" and self.items is None:
            self.__check_required_data("profile")

            soup = BeautifulSoup(self.profileHTML, 'html.parser')
            itemlinks = soup.select(".icon-quality")
            self.items = []

            for item in itemlinks:
                item_data = {}
                rel = item.find("a").get("rel")

                if rel is None:
                    item_data[itemNames[len(self.items)]] = {}
                else:
                    split = rel[0].split("&")
                    item_data[itemNames[len(self.items)]] = {"item": split[0].replace("item=", "")}

                    try:
                        if split[1].startswith("ench"):
                            item_data[itemNames[len(self.items)]]["ench"] = split[1].replace("ench=", "")
                        elif split[1].startswith("gem"):
                            item_data[itemNames[len(self.items)]]["gems"] = [i for i in split[1].replace("gems=", "").split(":") if i != "0"]
                    except IndexError:
                        pass

                    if len(split) >= 3:
                        try:
                            if split[2].startswith("gem"):
                                item_data[itemNames[len(self.items)]]["gems"] = [i for i in split[2].replace("gems=", "").split(":") if i != "0"]
                        except IndexError:
                            pass

                self.items.append(item_data)

        return True

    @check_error
    @check_required_data("items")
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
        #weaponSum = 0
        #weaponSum += sum(int(weapon['gs']) for weapon in weapons)
        if len(weapons) == 2:
            gs += math.floor(( int(weapons[0]['gs'])+ int(weapons[1]['gs']))/2 )
        elif len(weapons) == 1:
            gs += int(weapons[0]['gs'])
        return str(int(gs)) #XD

    @check_error
    @check_required_data("profile")
    def getGuild(self):
        try:
            soup = BeautifulSoup(self.profileHTML, 'html.parser')
            element = soup.select_one(".guild-name")
            result = element.get_text()
            return result
        except:
            return "None"

    @check_error
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

    @check_error
    @check_required_data("profile")
    def getAchivPts(self):
        try:
            soup = BeautifulSoup(self.profileHTML, 'html.parser')
            element = soup.select_one(".achievement-points")
            if element:
                return element.get_text().strip("[]")
            else:
                return "None"
        except:
            return "None"
        
    @check_error
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

    @check_error
    @check_required_data("profile")
    def getSpec(self):
        try:
            soup = BeautifulSoup(self.profileHTML, 'html.parser')
            element = soup.select_one(".specialization")
            name = element.select(".text")
            result = ""
            
            for i, item in enumerate(name):
                skillName = item.get_text()
                splitStr = skillName.split()
                skill = " ".join(splitStr)
                result += f"[{i+1}] {skill}\n"
            
            return result
        except:
            return "None"
    
    @check_error
    @check_required_data("items")
    def getEnchants(self):
        items = self.items 
        professions = self.getProfessions()
        cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))

        class_ = self.getLevelRace().split()[-1].strip()

        bannedItems = {1, 5, 6, 9, 14, 15}
        missingEnchants = []

        for i, item in enumerate(items):
            if i not in bannedItems:
                try:
                    if 'item' in item[itemNames[i]]:
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

        if class_ == "Death Knight" and False:
            pass

        if missingEnchants:
            return "Missing enchants from: " + ", ".join(missingEnchants)
        else:
            return "All items are enchanted!"
    
    @check_error
    @check_required_data("items")
    def getGems(self):
        items = self.items 
        professions = self.getProfessions()
        cleanprofessions = re.findall("([a-zA-Z]+)", str(professions))

        class_ = self.getLevelRace().split()[-1].strip()

        bannedItems = {1, 5, 6, 14, 15}
        missingGems = []

        for i, item in enumerate(items):
            if i not in bannedItems:
                try:
                    if 'item' in item[itemNames[i]]:
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

    @check_error
    @check_required_data("talents")
    def getGlyphs(self, glyphType):
        soup = BeautifulSoup(self.talentHTML, 'html.parser')
        glyphs = soup.select(f"div[data-glyphs]")
        result = [""] * 4

        for i, glyphset in enumerate(glyphs):
            b = glyphset.select(f".glyph.{glyphType}")
            for glyph in b:
                x = glyph.get_text().replace("\n", "")
                result[i] = result[i] + x + "\n"

        return result

    @check_error
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
        content = None
        try:
            content = json.loads(res)
        except json.JSONDecodeError:
            self.error = True
        
        if content != None and self.error == False:
            return content['content'] 
        if content == None or self.error == True:
            return None
        
    @check_error
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
            15001 : ["#ach3918", "#ach3917"],
            15002 : ["#ach3812", "#ach3916"],
            14961 : [],
            14962 : [],
            14922 : ["#ach4818", "#ach4817"],
            14923 : ["#ach4816", "#ach4815"],
        }
        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        if data == None:
            return
        soup = BeautifulSoup(data, 'html.parser')
        for class_name in list_of_achivs[list_of_instances[instance]]:
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
        return result

    @check_error
    def getICCAchiv(self, instance):
        list_of_instances = {
            "icc10" :15041,
            "icc25" :15042,
        }
        list_of_achivs = {
            15041 : ["#ach4531", "#ach4628", "#ach4528", "#ach4629",
                    "#ach4529", "#ach4630", "#ach4527", "#ach4631",
                    "#ach4530", "#ach4583"],
                    
            15042 : ["#ach4604", "#ach4632", "#ach4605", "#ach4633",
                    "#ach4606", "#ach4634", "#ach4607", "#ach4635",
                    "#ach4597", "#ach4584"],
        }
        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        if data == None:
            return
        soup = BeautifulSoup(data, 'html.parser')
        for i, class_name in enumerate(list_of_achivs[list_of_instances[instance]]):
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
        
        return result
    
    @check_error
    def getRSAchiv(self, instance):
        list_of_instances = {
            "naxx10" : 14922,
            "naxx25" : 14923
        }
        list_of_achivs = {
            14922 : ["#ach4817", "#ach4818"],
                    
            14923 : ["#ach4815", "#ach4816"],
        }
        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        if data == None:
            return
        soup = BeautifulSoup(data, 'html.parser')
        for i, class_name in enumerate(list_of_achivs[list_of_instances[instance]]):
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
        
        return result
    
    @check_error
    def getUlduarAchiv(self, instance):
        list_of_instances = {
            "uld10" : 14961,
            "uld25" : 14962,
        }
        list_of_achivs = {
            14961 : ["#ach2886", "#ach2888", "#ach2890", "#ach2892"],
                    
            14962 : ["#ach2887", "#ach2889", "#ach2889", "#ach2893"],
        }
        list_of_achivs_hm = { #Council, Hodir, Thorim, Freya, Mimimron, 2-1 Lights, Algalon, Herald
            14961 : ["#ach2941","#ach3182", "#ach3176", "#ach3179", "#ach3180",
                      "#ach3158" , "#ach3159", "#ach3158", "#ach3316"],
                    
            14962 : ["#ach2944", "#ach3184", "#ach3183", "#ach3187", "#ach3189",
                     "#ach3163", "#ach3164", "#ach3037"],
        }
        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        if data == None:
            return
        soup = BeautifulSoup(data, 'html.parser')
        for i, class_name in enumerate(list_of_achivs[list_of_instances[instance]]):
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
        result = result + "Hard Modes: \n"
        for i, class_name in enumerate(list_of_achivs_hm[list_of_instances[instance]]):
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
        
        return result
    
    @check_error
    def getNaxxAchiv(self, instance):
        list_of_instances = {
            "naxx10" : 14922,
            "naxx25" : 14923
        }
        list_of_achivs = { #Sarth, 1,2,3 - Spider, Construct, Plague, Mil, KT
                            #Undying, Malygos
            14922 : ["#ach1876", "#ach2049", "#ach2050", "#ach2051",
                    "#ach562", "#ach564", "#ach566", "#ach566",
                    "#ach574", "#ach2187", "#ach622"],
                    
            14923 : ["#ach625", "#ach2052", "#ach2053", "#ach2054",
                    "#ach563", "#ach563", "#ach567", "#ach569",
                    "#ach575", "#ach575", "#ach623"],
        }
        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        if data == None:
            return
        soup = BeautifulSoup(data, 'html.parser')
        for i, class_name in enumerate(list_of_achivs[list_of_instances[instance]]):
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
        
        return result
    
    @check_error
    def getTocAchiv(self, instance):
        list_of_instances = {
            "toc10" : 15001,
            "toc25" : 15002,
        }
        list_of_achivs = {
            15001 : ["#ach3917", "#ach3918", "#ach3808", "#ach3809","#ach3810", "#ach4080"],
                    
            15002 : ["#ach3916", "#ach3812", "#ach3817", "#ach3818","#ach3819"],
        }

        result = ""
        data = self.requestAchivCategory(list_of_instances[instance])
        if data == None:
            return
        soup = BeautifulSoup(data, 'html.parser')
        for i, class_name in enumerate(list_of_achivs[list_of_instances[instance]]):
            elements = soup.select(class_name)
            for element in elements:
                if element.select_one(".date"):
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "✅ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"
                else:
                    clean_text = re.sub(r'\s*\(\d+ player\)', '', str(element.select_one(".title").get_text()))
                    result = result + "❌ " + clean_text + "\n"
                    if i % 2:
                        result = result + "\n"

        if instance == "toc25":
        #We check FoS for immortality achi
            data1 = self.requestAchivCategory(81)
            soup = BeautifulSoup(data1, 'html.parser')
            elements = soup.select("#ach4079")
            if len(elements) == 1:
                result = result + "✅ " + "A Tribute to Immortality" + "\n"
            else:
                result = result + "❌ " + "A Tribute to Immortality" + "\n"

        return result