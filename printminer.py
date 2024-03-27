"""
Print Miner Discord Bot Game

This Python script contains the code for a Discord bot game called "Print Miner". 
The game includes various features such as mining, fighting, shopping, and leveling up.

The script uses the discord.py library to interact with Discord's API and asyncio for asynchronous tasks.

This program is a work in progress. More features will be added soon.

Author:
    Sonya C

Date:
    2/26/2024

Known Issues:
    - Docstrings to be fixed soon.
    - Leaving the game does not reset the shop. 
        - Will probably make Miner singleton as well.
    - Cancel buttons do not work properly.
    - Other Discord members can click on the buttons.
"""

import discord
import enum, random
import asyncio
import math

class DisplayCode(enum.IntEnum):
    LEVEL_UP = 0

    MINING_START = 1
    MINING = 2
    MINING_GOLD = 3
    MINING_COMPLETE = 4
    MINING_CANCELLED = 5
    MINING_CONTINUE = 6

    FIGHT_ENCOUNTER = 7
    FIGHT_ATTACK = 8 
    FIGHT_MINER_ATTACK = 9
    FIGHT_ENEMY_ATTACK = 10
    FIGHT_LOST = 11
    FIGHT_FLEE = 12
    FIGHT_FLEE_SUCCESS = 13
    FIGHT_FLEE_LOST = 14
    FIGHT_WIN = 15

    SHOP = 16
    BUY_HEAL = 17
    BUY_WEAPON = 18
    BUY_TOOL = 19
    UNAVAILABLE = 20 

    STATS = 21
    CANCEL = 22 

class Item():
    """
    Represents an item in the Print Miner game.

    Attributes:
        name (str): The name of the item.
        price (int): The price of the item in gold credits.

    Args:
        name (str): The name of the item.
        price (int): The price of the item in gold credits.
    """
    def __init__ (self, name: str, price: int):
        self.name = name
        self.price = price 

class Tool(Item):
    """
    Represents a tool in the Print Miner game. A tool is a type of item for mining.

    Attributes:
        mining_power (int): The mining power of the tool, which determines how effectively it can mine minerals.

    Args:
        name (str): The name of the tool.
        price (int): The price of the tool in gold credits.
        mining_power (int): The mining power of the tool.
    """
    def __init__(self, name: str, price: int, mining_power: int):
        super().__init__(name, price)
        self.mining_power = mining_power

class Weapon(Item):
    """
    Represents a weapon in the Print Miner game. A weapon is for fighting enemies.

    Attributes:
        damage (int): The damage of the weapon, which determines how much damage it can inflict in a fight.

    Args:
        name (str): The name of the weapon.
        price (int): The price of the weapon in gold credits.
        damage (int): The damage of the weapon.
    """
    def __init__(self, name: str, price: int, damage: int):
        super().__init__(name, price)
        self.damage = damage

    def get_lower_bound(self, upperbound: int) -> int:
        return round((4 * upperbound) / 5)

class Hammer(Weapon):
    def __init__ (self): 
        super().__init__("Hammer",0,20) # default tool

class HammerII(Weapon):
    def __init__ (self): 
        super().__init__("HammerII",0,30)

class UltraHam(Weapon):
    def __init__ (self): 
        super().__init__("UltraHam",0,50) 

class Pickaxe(Tool):
    def __init__ (self): 
        super().__init__("Pickaxe",0,1) # default tool

class PickaxeII(Tool):
    def __init__ (self): 
        super().__init__("PickaxeII",0,2) #TODO price = 250

class UltraPick(Tool):
    def __init__ (self): 
        super().__init__("UltraPick",0,3) #TODO price = 100

class NoMoreTools(Tool):
    def __init__ (self): 
        super().__init__("(out of stock)",0,0) #TODO price = 250

class Actor():
    """
    Represents an actor in the Print Miner game. An actor can be any character that performs actions in the game.
    Currently, the only actors are enemies.

    Attributes:
        name (str): The name of the actor.
        max_health (int): The maximum health of the actor.
        damage (int): The damage the actor can inflict.
        gold_credits (int): The amount of gold credits the actor has.

    Args:
        name (str): The name of the actor.
        max_health (int): The maximum health of the actor.
        damage (int): The damage the actor can inflict.
        gold_credits (int): The amount of gold credits the actor has.
    """
    def __init__(self, name: str, max_health: int, damage: int, gold_credits: int):
        self.name = name
        self.max_health = max_health
        self.damage = damage
        self.gold_credits = gold_credits

    def get_lower_bound(self, upperbound: int) -> int:
        return round((4 * upperbound) / 5)

class Miner():
    """
    Represents a miner in the Print Miner game.

    Attributes:
        name (str): The name of the miner.

        gold_credits (int): The amount of gold credits the miner has.

        health (int): The current health of the miner.

        max_health (int): The maximum health of the miner.

        weapon (Weapon): The weapon wielded by the miner.

        tool (Tool): The tool wielded by the miner.

        gold_found (int): The amount of gold found by the miner.

        experience (int): The experience points of the miner.

        game_over (bool): Whether the game is over for the miner.

        level (int): The current level of the miner.

    Args:
        name (str): The name of the miner.
    """
    def __init__ (self, name: str): 
        self.name = name
        self.gold_credits = 0
        self.health = 50
        self.max_health = 50
        self.weapon = Hammer()
        self.tool = Pickaxe() 
        self.gold_found = 0
        self.experience = 0
        self.game_over = False
        self.level = 1

    def heal (self) -> None:
        self.health = self.max_health

    def lose_credits (self, amount) -> None:
        self.gold_credits -= amount

    def weild_tool(self, tool: Tool):
        self.tool = tool

    def weild_weapon(self, weapon: Weapon):
        self.weapon = weapon

    async def level_up(self, interaction: discord.Interaction, miner):
        if self.experience >= self.level * 1000: # TODO level up health every 1000 experience, rounds to the nearest thousanth
            self.max_health += 10
            self.health = self.max_health
            self.level += 1
            self.experience = 0
            await LoadDisplays.display_miner(interaction, miner, DisplayCode.LEVEL_UP)
            
class Minerals():
    """
    Represents a mineral.

    Attributes:
        name (str): The name of the mineral.
        value (int): The value of the mineral in gold credits.

    Args:
        name (str): The name of the mineral.
        value (int): The value of the mineral in gold credits.
    """
    def __init__ (self, name, size, gold, experience):
        self.name = name
        self.size = size
        self.gold = gold
        self.experience = experience

    def get_lower_bound(self, upperbound) -> int:
        return round((4 * upperbound) / 5)
    
    def get_gold(self, miner: Miner) -> int:
        return round(random.randint(self.get_lower_bound(self.gold), self.gold) * math.log(miner.tool.mining_power,10))

class Rock(Minerals):
    def __init__ (self):
        super().__init__("rock",5,5,10)

class Stone(Minerals):
    def __init__ (self): 
        super().__init__("stone",10,10,20)

class Stone(Minerals):
    def __init__ (self): 
        super().__init__("gold",20,50,50)

class Stone(Minerals):
    def __init__ (self): 
        super().__init__("albamorium",50,10,20)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class Shop(metaclass=Singleton):
    """
    Represents a shop in the Print Miner game. The shop is a singleton, meaning there can only be one shop in the game.

    Attributes:
        tools (list): A list of tools available for purchase in the shop.
        weapons (list): A list of weapons available for purchase in the shop.
        current_tool (Tool): The tool currently being displayed in the shop.
        current_weapon (Weapon): The weapon currently being displayed in the shop.

    Methods:
        get_health_price(miner: Miner) -> int:
            Calculates the price of healing the miner based on their current health.
        display_tool() -> str:
            Returns a string representation of the current tool.
        display_weapon() -> str:
            Returns a string representation of the current weapon.
        display_health(miner: Miner) -> str:
            Returns a string representation of the miner's health and the cost to heal.
        purchase_health(miner: Miner) -> bool:
            Attempts to purchase health for the miner. Returns True if successful, False otherwise.
        purchase_tool(miner: Miner) -> bool:
            Attempts to purchase the current tool for the miner. Returns True if successful, False otherwise.
        purchase_weapon(miner: Miner) -> bool:
            Attempts to purchase the current weapon for the miner. Returns True if successful, False otherwise.
    """
    def __init__(self):
        self.tools: list = [PickaxeII(), UltraPick()]
        self.weapons: list = [HammerII(),UltraHam()]
        self.current_tool: Tool = self.tools[0]
        self.current_weapon: Weapon = self.weapons[0]

    def get_health_price(miner:Miner) -> int:
        return (miner.max_health - miner.health) * 10 

    def display_tool(self) -> str:
        return f"Tool : **{self.current_tool.name}** for {self.current_tool.price}"
    
    def display_weapon(self) -> str:
        return f"Weapon : **{self.current_weapon.name}** for {self.current_weapon.price}"
    
    def display_health(self, miner: Miner) -> str:
        if (miner.health == miner.max_health):
            return f"Health is full ! **{miner.health} / {miner.max_health}**"

        else:
            return f"Heal : **{miner.health} / {miner.max_health}** for {Shop.get_health_price(miner)}"
        
    def purchase_health(self, miner: Miner) -> bool:
        health_price = Shop.get_health_price(miner)
        if (miner.gold_credits >= health_price) and (miner.health != miner.max_health):
            miner.gold_credits -= health_price
            miner.heal()
            return True
        else:
            return False 
    
    def purchase_tool(self, miner: Miner) -> bool:
        if (miner.gold_credits >= self.current_tool.price) and (self.current_tool in self.tools):
            miner.weild_tool(self.current_tool)
            self.tools.remove(self.current_tool)  # Remove the purchased tool from the list

            if self.tools: # If there are still tools left
                self.current_tool = self.tools[0] # The next tool for sale
                return True
            else:
                self.current_tool = NoMoreTools()
                return True

        else:
            return False 
        
    def purchase_weapon(self, miner: Miner) -> bool:
        if (miner.gold_credits >= self.current_weapon.price) and (self.current_weapon in self.weapons):
            miner.weild_weapon(self.current_weapon)
            self.weapons.remove(self.current_weapon) 

            if self.weapons: 
                self.current_weapon = self.weapons[0] 
                return True
            else:
                self.current_weapon = NoMoreTools()
                return True

        else:
            return False 
    

class Enemy(Actor):
    def __init__ (self, name, health, damage, gold_credits): 
        super().__init__(name, health,damage, gold_credits)

class Bug(Enemy):
    def __init__ (self): 
        super().__init__("Bug",40,5,5)

class BigBug(Enemy):
    def __init__ (self): 
        super().__init__("Bug",80,20,10)

class Rockadillo(Enemy):
    def __init__ (self): 
        super().__init__("Rockadillo",100,30,20)

class Cadosaurus(Enemy):
    def __init__ (self): 
        super().__init__("Cadosaurus",90,10,90)

class LoadDisplays():
    async def display_interaction(interaction: discord.Interaction, miner: Miner, mineral: Minerals, display_code: DisplayCode) -> None:
        if (display_code == DisplayCode.MINING_START):
            view = CancelButton(miner,mineral)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Mining {mineral.name}",
                ), view = view
            )

        elif (display_code == DisplayCode.MINING):
            view = CancelButton(miner,mineral)
            await interaction.edit_original_response(embed = discord.Embed(
                title = f"Mining {mineral.name}",
                description = f"chunks remaining : {mineral.size} \n - "
                ), view = view
            )

        elif (display_code == DisplayCode.MINING_CANCELLED):
            view = LoadButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                title = f"Mining {mineral.name} ABORTED",
                description = f"chunks remaining : {mineral.size}, \n gold collected : {miner.gold_found}"
                ), view = view
            )
            miner.game_over = True

        elif (display_code == DisplayCode.MINING_GOLD):
            view = CancelButton(miner,mineral)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Mining {mineral.name}",
                    description = f"chunks remaining : {mineral.size} \n gold found!"
                ), view = view
            )

        elif (display_code == DisplayCode.MINING_COMPLETE):
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f" You have {miner.gold_credits} credits.",
                    description = f"Accumulated gold: {miner.gold_found} from {mineral.name}"
                ), view = None
            )

        elif (display_code == DisplayCode.MINING_CONTINUE):
            view = LoadButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f" You have {miner.gold_credits} credits.",
                    description = f"Accumulated gold: {miner.gold_found} from {mineral.name} continue?"
                ), view = view
            )
            
    # All responses to do with fighting
    async def display_fight(interaction: discord.Interaction, miner: Miner, enemy: Enemy, display_code: DisplayCode) -> None:

        if (display_code == DisplayCode.FIGHT_ENCOUNTER):
            view = FightButtons(miner, enemy)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"ENEMY ENCOUNTER : {enemy.name}",
                    description = f"Do you wish to fight or flee?" 
                ), view = view # TODO HAVE ABILITY TO SEE YOUR STATS AND ENEMY STATS
            )
        
        elif (display_code == DisplayCode.FIGHT_MINER_ATTACK):
            view = FleeButton(miner,enemy)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"You dealt {miner.weapon.damage} to {enemy.name}",
                    description = f"Your health : {miner.health} \ {miner.max_health}\n {enemy.name} health : {enemy.max_health}"
                ), view = view
            )
        elif (display_code == DisplayCode.FIGHT_ENEMY_ATTACK):
            view = FleeButton(miner,enemy)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"{enemy.name} attacked you with {enemy.damage} damage",
                    description = f"Your health : {miner.health} \ {miner.max_health}\n {enemy.name} health : {enemy.max_health}"
                ), view = view
            )
        elif (display_code == DisplayCode.FIGHT_WIN):
            view = LoadButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"You have killed {enemy.name} with {miner.weapon.damage} damage",
                    description = f"Your health : {miner.health} \ {miner.max_health}"
                ), view = view
            )

        elif (display_code == DisplayCode.FIGHT_LOST):
            view = GameOverButtons(miner)
            miner.game_over = True
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"{enemy.name} killed you with {enemy.damage} damage",
                    description = f"All your stats have been deleted"
                ), view = view
            )

    async def display_flee(interaction: discord.Interaction, miner: Miner, enemy: Enemy, display_code: DisplayCode):
        if (display_code == DisplayCode.FIGHT_FLEE_SUCCESS):
            view = LoadButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"You have ran away from {enemy.name}:",
                    description = f"Continue mine"
                ), view = view
            )

        elif(display_code == DisplayCode.FIGHT_FLEE_LOST):
            view = LoadButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"As you fled, the {enemy.name} stole {enemy.gold_credits} CREDITS:",
                    description = f"Mine elsewhere?"
                ), view = view
            )

    async def display_miner(interaction: discord.Interaction, miner: Miner, display_code: DisplayCode) -> None:
        if (display_code == DisplayCode.STATS):
            if miner.game_over == False:
                view = LoadButtons(miner)
            else: # if player died
                view = GameOverButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Your stats",
                    description = f" Health: {miner.health} \ {miner.max_health} \n {miner.tool.name} : {miner.tool.mining_power} mp \n Damage : {miner.weapon.damage} \n Credits : {miner.gold_credits} \n Experience : {miner.experience}"
                ), view = view
            )

        elif(display_code == DisplayCode.LEVEL_UP):
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Level up!",
                    description = f"Health: {miner.health} \ {miner.max_health}"
                ), view = None
            )

    async def display_shop(interaction: discord.Interaction, miner: Miner, shop: Shop, display_code: DisplayCode) -> None:
        if (display_code == DisplayCode.SHOP):
            view = ShopButtons(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Welcome to the Shop",
                    description = f"Your credits : {miner.gold_credits}\n\n  {Shop.display_health(shop,miner)} \n {Shop.display_weapon(shop)} \n {Shop.display_tool(shop)}"
                ), view = view
            )

        elif(display_code == DisplayCode.BUY_HEAL):
            view = ShopBackButton(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Purchased healing potion",
                    description = f"You have been healed. \n health : {miner.health} \ {miner.max_health}"
                ), view = view
            )

        elif(display_code == DisplayCode.BUY_WEAPON):
            view = ShopBackButton(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Purchased {miner.weapon.name}",
                    description = f"Your damage power is now {miner.weapon.damage} (dmg)"
                ), view = view
            )            
            miner.game_over = True

        elif(display_code == DisplayCode.BUY_TOOL):
            view = ShopBackButton(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"Purchased {miner.tool.name}",
                    description = f"Your mining power is now {miner.tool.mining_power} (mp)"
                ), view = view
            )
        
        elif(display_code == DisplayCode.UNAVAILABLE):
            view = ShopBackButton(miner)
            await interaction.edit_original_response(embed = discord.Embed(
                    title = f"You can't purchase that.",
                    description = f"*You may not have enough credits, or there are no more items to buy.*"
                ), view = view
            )

class LoadButtons(discord.ui.View):
    def __init__(self, miner: Miner):
        super().__init__(timeout = None)
        self.miner = miner
        self.shop = Shop()

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.success)
    async def start_mine(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await PrintMiner.mine(interaction, self.miner) # Pass the Miner object to the mine function

    @discord.ui.button(label="Shop", 
                       style=discord.ButtonStyle.blurple)
    async def shopping(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.SHOP)
        
    @discord.ui.button(label="Stats", 
                       style=discord.ButtonStyle.gray)
    async def stats(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_miner(interaction, self.miner, DisplayCode.STATS)

    @discord.ui.button(label="Abort", 
                       style=discord.ButtonStyle.red)
    async def cancel_mine(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await interaction.edit_original_response(
            embed = discord.Embed(
                title = "YOU HAVE LEFT",
            ), view = None
        )

class ShopButtons(discord.ui.View):
    def __init__(self, miner: Miner):
        super().__init__(timeout = None)
        self.miner = miner
        self.shop = Shop()

    @discord.ui.button(label = "Back",
                       style = discord.ButtonStyle.gray)
    async def back(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        view = LoadButtons(self.miner)
        await interaction.edit_original_response(
            embed = discord.Embed(
                title = "WELCOME",
            ), view = view
        )

    @discord.ui.button(label = "Buy Health",
                       style = discord.ButtonStyle.blurple)
    async def buy_health(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()

        if (self.shop.purchase_health(self.miner)):
            await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.BUY_HEAL)
        else:
            await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.UNAVAILABLE)


    @discord.ui.button(label = "Buy Weapon",
                       style = discord.ButtonStyle.blurple)
    async def buy_weapon(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()

        if (self.shop.purchase_weapon(self.miner)):
            await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.BUY_WEAPON)
        else:
            await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.UNAVAILABLE)

    @discord.ui.button(label = "Buy Tool",
                       style = discord.ButtonStyle.blurple)
    async def buy_tool(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()

        if (self.shop.purchase_tool(self.miner)):
            await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.BUY_TOOL)
        else:
            await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.UNAVAILABLE)

# Cancels mining but not the game.
class CancelButton(discord.ui.View):
    def __init__(self, miner, mineral):
        super().__init__(timeout = None)
        self.miner = miner
        self.mineral = mineral

    @discord.ui.button(label = "Cancel",
                       style = discord.ButtonStyle.red)
    async def cancel_mine(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_interaction(interaction, self.miner, self.mineral, DisplayCode.MINING_CANCELLED)

class ShopBackButton(discord.ui.View):
    def __init__(self, miner: Miner):
        super().__init__(timeout = None)
        self.miner = miner
        self.shop = Shop()

    @discord.ui.button(label = "Back",
                       style = discord.ButtonStyle.gray)
    async def back(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_shop(interaction, self.miner, self.shop, DisplayCode.SHOP)

# Allows user to flee during battle.
class FleeButton(discord.ui.View):
    def __init__(self, miner, enemy):
        super().__init__(timeout = None)
        self.miner = miner
        self.enemy = enemy

    @discord.ui.button(label = "Flee",
                       style = discord.ButtonStyle.success)
    async def flee(self, interaction: discord.Interaction, button:discord.ui.Button)  -> None:
        await interaction.response.defer()
        await PrintMiner.miner_flee(interaction, self.miner, self.enemy) 

# Upon encountering an enemy, the user has the option to begin the fighting loop or flee. 
class FightButtons(discord.ui.View):
    def __init__(self, miner, enemy):
        super().__init__(timeout = None)
        self.miner = miner
        self.enemy = enemy

    @discord.ui.button(label = "Flee",
                       style = discord.ButtonStyle.success)
    async def flee(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await PrintMiner.miner_flee(interaction, self.miner, self.enemy) # begins flee

    @discord.ui.button(label = "Attack",
                       style = discord.ButtonStyle.red)
    async def fight(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await PrintMiner.enemy_attack(interaction, self.miner, self.enemy) # begins fight 

# Loads when player dies
class GameOverButtons(discord.ui.View):
    def __init__(self, miner: Miner):
        super().__init__(timeout = None)
        self.miner = miner

    @discord.ui.button(label="Stats", style=discord.ButtonStyle.gray)
    async def stats(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_miner(interaction, self.miner, DisplayCode.STATS)

    @discord.ui.button(label="Abort", style=discord.ButtonStyle.red)
    async def cancel_mine(self, interaction: discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.defer()
        await interaction.edit_original_response(
            embed = discord.Embed(
                title = "YOU HAVE LEFT",
                description = f"yes...all stats have been deleted." 
            ), view = None
        )

class PrintMiner:
    def setup_miner() -> Miner:
        miner: Miner = Miner("Miner") #TODO, give player option to name. Name will be adressed in the shop
        return miner
    
    def setup_enemy() -> Enemy:
        enemy_type: Enemy = random.choice(Enemy.__subclasses__())()
        return enemy_type
    

    @staticmethod
    async def mine(interaction : discord.Interaction, miner:Miner) -> None:
        mineral_type: Minerals = random.choice(Minerals.__subclasses__())()
        mineral_size: int = random.randint(mineral_type.get_lower_bound(mineral_type.size), mineral_type.size)
        mineral_gold: int = random.randint(mineral_type.get_lower_bound(mineral_type.gold), mineral_type.gold) * miner.tool.mining_power
        mineral_experience: int = random.randint(mineral_type.get_lower_bound(mineral_type.experience), mineral_type.experience)
        mineral_gold_count: int = 0
        miner.gold_found = 0 # resets the amount of gold.
        miner.game_over = False

        # Creates a list of the chunks to be displayed as a count down.
        chunk_count: list = [chunk for chunk in range(mineral_size,0,-abs(miner.tool.mining_power))]

        await LoadDisplays.display_interaction(interaction, miner, mineral_type, DisplayCode.MINING_START)
        await asyncio.sleep(.5)

        for chunk in chunk_count:
            if miner.game_over == False:
                mineral_type.size = chunk # updating mineral size to be displayed 
                await asyncio.sleep(0)
                await LoadDisplays.display_interaction(interaction, miner, mineral_type, DisplayCode.MINING) # The cancel display may set game_over to true

                # Display gold found
                if random.random() < .60 and miner.game_over == False: # 60% chance of gold
                    print("DEBUG: adding gold...")
                    miner.gold_credits += mineral_gold
                    mineral_gold_count += 1
                    await LoadDisplays.display_interaction(interaction, miner, mineral_type, DisplayCode.MINING_GOLD)

                miner.gold_found = mineral_gold_count * mineral_gold # calculate the amount of gold found in mineral.
                miner.experience += mineral_experience

            else:
                break # if the for loop stops iterating if the game is over.

            await miner.level_up(interaction, miner) # checks if miner can level up and displays level up message.

        # Initiate and display encounter after mining mineral.
        if random.random() < .50 and miner.game_over == False: # 50% chance of enemy
            await LoadDisplays.display_interaction(interaction, miner, mineral_type, DisplayCode.MINING_COMPLETE)
            enemy_type = PrintMiner.setup_enemy()
            await asyncio.sleep(.5)

            await LoadDisplays.display_fight(interaction, miner, enemy_type, DisplayCode.FIGHT_ENCOUNTER)
            print("DEBUG: encounter")
        else:
            await LoadDisplays.display_interaction(interaction, miner, mineral_type, DisplayCode.MINING_CONTINUE)
            print("DEBUG: continue mine")


    async def enemy_attack(interaction: discord.Interaction, miner: Miner, enemy: Enemy) -> None:
        enemy.max_health = random.randint(enemy.get_lower_bound(enemy.max_health), enemy.max_health)
        turn: int = random.randint(0,1)
        
        while (enemy.max_health > 0 and miner.health > 0):
            print("DEBUG: in fight loop")
            if (turn == 0): # enemy attack
                enemy.damage = random.randint(enemy.get_lower_bound(enemy.damage), enemy.damage)
                miner.health -= enemy.damage

                await asyncio.sleep(1)

                if (miner.health < 0): # health should not be negative
                    miner.health = 0   

                await LoadDisplays.display_fight(interaction, miner, enemy, DisplayCode.FIGHT_ENEMY_ATTACK)
                print("DEBUG: enemy turn")
                turn += 1

            elif(turn == 1): # player turn   
                miner_damage = random.randint(miner.weapon.get_lower_bound(miner.weapon.damage), miner.weapon.damage)
                miner.weapon.damage = miner_damage         
                enemy.max_health -= miner_damage

                await asyncio.sleep(1)

                if (enemy.max_health < 0):
                    enemy.max_health = 0

                await LoadDisplays.display_fight(interaction, miner, enemy, DisplayCode.FIGHT_MINER_ATTACK)
                print("DEBUG: player turn")
                turn -= 1 

        print("DEBUG: Leave fight loop")
        if (enemy.max_health == 0):
            await asyncio.sleep(1)
            await LoadDisplays.display_fight(interaction, miner, enemy, DisplayCode.FIGHT_WIN)
            print("DEBUG: player win")

        elif (miner.health == 0):
            await asyncio.sleep(1)
            await LoadDisplays.display_fight(interaction, miner, enemy, DisplayCode.FIGHT_LOST)
            miner.game_over = True
            print("DEBUG: player lost")

    # When the miner flees there is a chance to lose gold_credits.
    async def miner_flee(interaction: discord.Interaction, miner: Miner, enemy: Enemy) -> None: 

        if (random.random() < .30): # 30% chance
            miner.gold_credits -= enemy.gold_credits
            await LoadDisplays.display_flee(interaction, miner, enemy, DisplayCode.FIGHT_FLEE_LOST )
            await asyncio.sleep(1)
        else:
            await LoadDisplays.display_flee(interaction, miner, enemy, DisplayCode.FIGHT_FLEE_SUCCESS)
            await asyncio.sleep(1)