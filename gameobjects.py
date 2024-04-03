"""all print miner objects"""
import random
import math

class Singleton(type):
    """Used in the Shop and Miner class

    Args:
        type (_type_): _description_

    Returns:
        _type_: _description_
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

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

class Miner(metaclass=Singleton):
    """
    Represents a miner in the Print Miner game. 
    
    There can only be one instance of the miner per game.

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
    """
    def __init__ (self): 
        self.name = "[MINER]"
        self.gold_credits = 0
        self.health = 50
        self.max_health = 50
        self.weapon = Hammer()
        self.tool = Pickaxe() 
        self.gold_found = 0
        self.experience = 0
        self.game_over = False
        self.level = 1

    def reset(self):
        """Resets all attributes of the Miner once the user aborts the game."""
        self.name = "[MINER]"
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
        """Miner health is set to the maximum health."""
        self.health = self.max_health

    def lose_credits (self, amount: int) -> None:
        """
        Miner loses credits based on specified amount.
        Ensures that credits can not be negative.

        Args:
            amount (int): The amount of credits to lose.
        """
        self.gold_credits -= amount
        if self.gold_credits < 0:
            self.gold_credits = 0

    def lose_health(self, amount: int):
        """
        Miner loses health based on specified amount.
        Ensures that health can not be negative.

        Args:
            amount (int): The amount of health to lose.
        """
        if amount > self.health:
            self.health = 0
        else: 
            self.health -= amount

    def weild_tool(self, tool: Tool) -> None:
        """
        Miner weilds a Tool object by replacing their current Tool with another.

        Args:
            tool (Tool): The tool the player will weild.
        """
        self.tool = tool

    def weild_weapon(self, weapon: Weapon) -> None:
        """
        Miner weilds a Weapon object by replacing their current Weapon with another.

        Args:
            weapon (Weapon): The weapon the player will weild.
        """
        self.weapon = weapon

    def level_up(self) -> bool:
        """
        The Miner levels up every 1000 experience points. 
        """
        if self.experience >= self.level * 10: #TODO make 1000
            self.max_health += 10
            self.health = self.max_health
            self.level += 1
            self.experience = 0
            return True

        else:
            return False
        
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
        super().__init__("albamorium",35,10,20)

class Stone(Minerals):
    def __init__ (self): 
        super().__init__("igsite",10,10,1)
        
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
        
class Actor():
    """
    Represents an actor in the Print Miner game. 
    
    An actor can be any character that performs actions in the game.
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
    
    def lose_health(self, amount: int):
        """
        Actor loses health based on specified amount.
        Ensures that health can not be negative.

        Args:
            amount (int): The amount of health to lose.
        """
        if amount > self.max_health:
            self.max_health = 0
        else: 
            self.max_health -= amount

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

