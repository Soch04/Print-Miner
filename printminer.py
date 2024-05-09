"""
Print Miner Discord Bot Game

This Python script contains the code for a Discord bot game called "Print Miner". 
The game includes various features such as mining, fighting, shopping, and leveling up.

The script uses asyncio and the discord.py library to interact with Discord's API.

Author:
    Sonya C

Date updated:
    5/09/2024
"""

import asyncio
import enum
import random
from gameobjects import Miner, Shop, Enemy, Minerals
from StringProgressBar import progressBar
import discord


class DisplayCode(enum.IntEnum):
    """Enum class to represent different Print Miner response types through Discord."""

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
    ABORT = 23


class Final(enum.IntEnum):
    "Holds final values."
    BUTTON_TIMEOUT = 30  # seconds


class LoadDisplays:
    """Handles the display of interactions, fights, miner stats, and shop transactions."""

    @staticmethod
    async def display_mining_progress(
        interaction: discord.Interaction,
        miner: Miner,
        mineral: Minerals,
        progress_bar: str,
        display_code: DisplayCode,
    ) -> None:
        """
        Handles the display of mining progress in the game.

        Args:
            interaction (discord.Interaction): The Discord interaction that triggered the display.
            miner (Miner): The Miner instance involved in the interaction.
            mineral (Minerals): The Minerals instance being mined.
            progress_bar (str): The progress bar string to be displayed.
            display_code (DisplayCode): The code indicating the specific display to be shown.
        """
        if display_code == DisplayCode.MINING:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"Mining {mineral.name} | Gold : {miner.gold_found}",
                    description=f"```css\n chunks remaining : {mineral.size}" 
                    + f"\n {progress_bar}\n Miner Lvl : {miner.level}```"
                ),
                view=None,
            )

    @staticmethod
    async def display_interaction(
        interaction: discord.Interaction,
        miner: Miner,
        mineral: Minerals,
        display_code: DisplayCode,
    ) -> None:
        """
        Handles the display of mining interactions in the game.

        Args:
            interaction (discord.Interaction): The Discord interaction that triggered the display.
            miner (Miner): The Miner instance involved in the interaction.
            mineral (Minerals): The Minerals instance being mined.
            display_code (DisplayCode): The code indicating the specific display to be shown.
        """
        if display_code == DisplayCode.MINING_START:
            view = CancelButton(mineral)
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"Mining {mineral.name}",
                ),
                view=view,
            )
        elif display_code == DisplayCode.MINING_CANCELLED:
            view = MenuButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"Mining {mineral.name} ABORTED",
                    description=f"chunks remaining : {mineral.size}"
                    + f"\n gold collected : {miner.gold_found}"
                ),
                view=view,
            )
        elif display_code == DisplayCode.MINING_COMPLETE:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f" You have {miner.gold_credits} credits.",
                    description=f"Accumulated gold: {miner.gold_found} from {mineral.name}",
                ),
                view=None,
            )
        elif display_code == DisplayCode.MINING_CONTINUE:
            view = MenuButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f" You have {miner.gold_credits} credits.",
                    description=f"Accumulated gold: {miner.gold_found}"
                    + f"from {mineral.name} continue?"
                ),
                view=view,
            )

    # All responses to do with fighting
    @staticmethod
    async def display_fight(
        interaction: discord.Interaction,
        miner: Miner,
        enemy: Enemy,
        display_code: DisplayCode,
    ) -> None:
        """
        Handles the display of fight interactions in the game.

        Buttons: FightButton(), FleeButton(), MenuButtons(), GameOverButtons()

        Args:
            interaction (discord.Interaction): The Discord interaction that triggered the display.
            miner (Miner): The Miner instance involved in the fight.
            enemy (Enemy): The Enemy instance involved in the fight.
            display_code (DisplayCode): The code indicating the specific display to be shown.
        """

        if display_code == DisplayCode.FIGHT_ENCOUNTER:
            view = FightButtons(enemy)
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"ENEMY ENCOUNTER : {enemy.name}",
                    description="Do you wish to fight or flee?",
                ),
                view=view,
            )
        elif display_code == DisplayCode.FIGHT_MINER_ATTACK:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"You dealt {miner.weapon.damage} to {enemy.name}",
                    description=f"\nYour health : {miner.health} \ {miner.max_health}"
                                + f"\n {enemy.name} health : {enemy.max_health}"
                ),
                view=None,
            )
        elif display_code == DisplayCode.FIGHT_ENEMY_ATTACK:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"{enemy.name} attacked you with {enemy.damage} damage",
                    description=f"\nYour health : {miner.health} \ {miner.max_health}"
                                + f"\n {enemy.name} health : {enemy.max_health}",
                ),
                view=None,
            )
        elif display_code == DisplayCode.FIGHT_WIN:
            view = MenuButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"You have killed {enemy.name} with {miner.weapon.damage} damage",
                    description=f"Your health : {miner.health} \ {miner.max_health}",
                ),
                view=view,
            )
        elif display_code == DisplayCode.FIGHT_LOST:
            view = GameOverButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"{enemy.name} killed you with {enemy.damage} damage",
                    description="All your stats have been deleted",
                ),
                view=view,
            )

    @staticmethod
    async def display_flee(
        interaction: discord.Interaction,
        miner: Miner,
        enemy: Enemy,
        display_code: DisplayCode,
    ):
        """
        Handles the display of flee interactions in the game.

        Args:
            interaction (discord.Interaction): The Discord interaction that triggered the display.
            miner (Miner): The Miner instance attempting to flee.
            enemy (Enemy): The Enemy instance involved in the interaction.
            display_code (DisplayCode): The code indicating the specific display to be shown.
        """
        if display_code == DisplayCode.FIGHT_FLEE_SUCCESS:
            view = MenuButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"You have ran away from {enemy.name}:",
                    description="Continue mine",
                ),
                view=view,
            )
        elif display_code == DisplayCode.FIGHT_FLEE_LOST:
            view = MenuButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"As you fled, the {enemy.name} stole {enemy.gold_credits} CREDITS:",
                    description=f"Credits remaining : {miner.gold_credits} \n Mine elsewhere?",
                ),
                view=view,
            )

    @staticmethod
    async def display_miner(
        interaction: discord.Interaction, miner: Miner, display_code: DisplayCode
    ) -> None:
        """
        Handles the display of miner stats in the game.

        Args:
            interaction (discord.Interaction): The Discord interaction that triggered the display.
            miner (Miner): The Miner instance whose stats are to be displayed.
            display_code (DisplayCode): The code indicating the specific display to be shown.
        """
        if display_code == DisplayCode.STATS:
            if miner.game_over is False:
                view = MenuButtons()
            else:  # if player died
                view = GameOverButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Your stats",
                    description=f" Health: {miner.health} \ {miner.max_health}"
                    + f"\n {miner.tool.name} : {miner.tool.mining_power} mp"
                    + f"\n {miner.weapon.name} : {miner.weapon.damage} dmg"
                    + f"\n Credits : {miner.gold_credits}"
                    + f"\n Experience : {miner.experience}"
                    + f"\n Level : {miner.level}",
                ),
                view=view,
            )
        elif display_code == DisplayCode.LEVEL_UP:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Level up!",
                    description=f"Health: {miner.health} \ {miner.max_health}",
                ),
                view=None,
            )
        elif display_code == DisplayCode.ABORT:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="ABORTED GAME", description="All stats have been deleted"
                ),
                view=None,
            )

    @staticmethod
    async def display_shop(
        interaction: discord.Interaction,
        miner: Miner,
        shop: Shop,
        display_code: DisplayCode,
    ) -> None:
        """
        Handles the display of shop transactions in the game.

        Args:
            interaction (discord.Interaction): The Discord interaction that triggered the display.
            miner (Miner): The Miner instance involved in the transaction.
            shop (Shop): The Shop instance where the transaction is taking place.
            display_code (DisplayCode): The code indicating the specific display to be shown.
        """
        if display_code == DisplayCode.SHOP:
            view = ShopButtons()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Welcome to the Shop",
                    description=f" Your credits : {miner.gold_credits}\n"
                    + f"\n {Shop.display_health(shop,miner)}"
                    + f"\n {Shop.display_weapon(shop)}"
                    + f"\n {Shop.display_tool(shop)}",
                ),
                view=view,
            )
        elif display_code == DisplayCode.BUY_HEAL:
            view = ShopBackButton()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Purchased healing potion",
                    description=f"You have been healed. \n health : {miner.health} \ {miner.max_health}",
                ),
                view=view,
            )
        elif display_code == DisplayCode.BUY_WEAPON:
            view = ShopBackButton()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"Purchased {miner.weapon.name}",
                    description=f"Your damage power is now {miner.weapon.damage} (dmg)",
                ),
                view=view,
            )
        elif display_code == DisplayCode.BUY_TOOL:
            view = ShopBackButton()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"Purchased {miner.tool.name}",
                    description=f"Your mining power is now {miner.tool.mining_power} (mp)",
                ),
                view=view,
            )
        elif display_code == DisplayCode.UNAVAILABLE:
            view = ShopBackButton()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="You can't purchase that.",
                    description="*Not enough credits or item is out of stock*",
                ),
                view=view,
            )


class MenuButtons(discord.ui.View):
    """Includes buttons for mining, shopping, viewing stats, and aborting the game."""

    def __init__(self):
        super().__init__(timeout=Final.BUTTON_TIMEOUT)
        self.miner = Miner()
        self.shop = Shop()
        self.miner.game_over = False

    @discord.ui.button(label="Mine", style=discord.ButtonStyle.success)
    async def start_mine(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await PrintMiner.mine(
            interaction, self.miner
        )  # Pass the Miner object to the mine function

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.blurple)
    async def shopping(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_shop(
            interaction, self.miner, self.shop, DisplayCode.SHOP
        )

    @discord.ui.button(label="Stats", style=discord.ButtonStyle.gray)
    async def stats(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_miner(interaction, self.miner, DisplayCode.STATS)

    @discord.ui.button(label="Abort", style=discord.ButtonStyle.red)
    async def abort(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        self.miner.reset()  # Reset the miner stats
        self.shop.reset()
        await LoadDisplays.display_miner(interaction, self.miner, DisplayCode.ABORT)


class ShopButtons(discord.ui.View):
    """Includes buttons for returning to the main menu, buying health, weapons, and tools."""

    def __init__(self):
        super().__init__(timeout=Final.BUTTON_TIMEOUT)
        self.miner = Miner()
        self.shop = Shop()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
    async def back(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        view = MenuButtons()
        await interaction.edit_original_response(
            embed=discord.Embed(
                title="WELCOME",
            ),
            view=view,
        )

    @discord.ui.button(label="Buy Health", style=discord.ButtonStyle.blurple)
    async def buy_health(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()

        if self.shop.purchase_health(self.miner):
            await LoadDisplays.display_shop(
                interaction, self.miner, self.shop, DisplayCode.BUY_HEAL
            )
        else:
            await LoadDisplays.display_shop(
                interaction, self.miner, self.shop, DisplayCode.UNAVAILABLE
            )

    @discord.ui.button(label="Buy Weapon", style=discord.ButtonStyle.blurple)
    async def buy_weapon(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()

        if self.shop.purchase_weapon(self.miner):
            await LoadDisplays.display_shop(
                interaction, self.miner, self.shop, DisplayCode.BUY_WEAPON
            )
        else:
            await LoadDisplays.display_shop(
                interaction, self.miner, self.shop, DisplayCode.UNAVAILABLE
            )

    @discord.ui.button(label="Buy Tool", style=discord.ButtonStyle.blurple)
    async def buy_tool(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()

        if self.shop.purchase_tool(self.miner):
            await LoadDisplays.display_shop(
                interaction, self.miner, self.shop, DisplayCode.BUY_TOOL
            )
        else:
            await LoadDisplays.display_shop(
                interaction, self.miner, self.shop, DisplayCode.UNAVAILABLE
            )


class CancelButton(discord.ui.View):
    """Button allows the user to cancel mining operation before it starts."""

    def __init__(self, mineral: Minerals):
        super().__init__(timeout=Final.BUTTON_TIMEOUT)
        self.miner = Miner()
        self.mineral = mineral

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_mine(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        self.miner.game_over = True
        await LoadDisplays.display_interaction(
            interaction, self.miner, self.mineral, DisplayCode.MINING_CANCELLED
        )


class ShopBackButton(discord.ui.View):
    """Button which allows the user to go back to the main shop menu."""

    def __init__(self):
        super().__init__(timeout=None)
        self.miner = Miner()
        self.shop = Shop()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
    async def back(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_shop(
            interaction, self.miner, self.shop, DisplayCode.SHOP
        )


class FightButtons(discord.ui.View):
    """Includes buttons for fleeing and attacking when the user encounters an enemy."""

    def __init__(self, enemy: Enemy):
        super().__init__(timeout=Final.BUTTON_TIMEOUT)
        self.miner = Miner()
        self.enemy = enemy

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.success)
    async def flee(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await PrintMiner.miner_flee(interaction, self.miner, self.enemy)  # begins flee

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.red)
    async def fight(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await PrintMiner.enemy_attack(
            interaction, self.miner, self.enemy
        )  # begins fight


class GameOverButtons(discord.ui.View):
    """
    Includes buttons for viewing stats and aborting the game.
    This is called when the Miner dies.
    """

    def __init__(self):
        super().__init__(timeout=Final.BUTTON_TIMEOUT)
        self.miner = Miner()
        self.shop = Shop()

    @discord.ui.button(label="Stats", style=discord.ButtonStyle.gray)
    async def stats(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await LoadDisplays.display_miner(interaction, self.miner, DisplayCode.STATS)

    @discord.ui.button(label="Abort", style=discord.ButtonStyle.red)
    async def cancel_mine(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        self.miner.reset()  # Reset the miner stats
        self.shop.reset()
        await LoadDisplays.display_miner(interaction, self.miner, DisplayCode.ABORT)


class PrintMiner:
    """Sets up the Miner and Enemy objects and handles game loop and logic for Print Miner."""

    @staticmethod
    def setup_miner() -> Miner:
        """Returns Miner object"""
        miner: Miner = Miner()
        return miner

    @staticmethod
    def setup_enemy() -> Enemy:
        """Returns Enemy object"""
        enemy_type: Enemy = random.choice(Enemy.__subclasses__())()
        return enemy_type

    @staticmethod
    async def mine(interaction: discord.Interaction, miner: Miner) -> None:
        """
        This function simulates the mining process in the game. It randomly selects a
        mineral type and size. Then it initiates a mining process where the miner
        extracts chunks of the mineral until depleted.

        During the mining process, a progress bar displays the mining progress. The
        miner may also find gold (credits) during mining. After the mining process,
        there's a chance to initiate an enemy encounter.

        Args:
            interaction (discord.Interaction): The interaction object that represents a
                user's interaction (like a command invocation) with the bot.
            miner (Miner): The miner object that will perform the mining.
        """

        # Setting up variables
        mineral_type: Minerals = random.choice(Minerals.__subclasses__())()
        mineral_size: int = random.randint(
            mineral_type.get_lower_bound(mineral_type.size), mineral_type.size
        )
        mineral_gold: int = (
            random.randint(
                mineral_type.get_lower_bound(mineral_type.gold), mineral_type.gold
            )
            * miner.tool.mining_power
        )
        mineral_experience: int = random.randint(
            mineral_type.get_lower_bound(mineral_type.experience),
            mineral_type.experience,
        )
        mineral_gold_count: int = 0
        miner.gold_found = 0  # Resets the amount of gold.
        miner.game_over = False

        # CREATING A STRING PROGRESS BAR:
        #   progress_bar_length of the progress bar is equivalent to the size of the mineral.
        #   progress_bar_current represents the current length of the filled.
        #   portion of the progress bar.
        #   progress_bar[0] returns the string state of the progress bar.

        #   The progress bar is based on the chunk count.

        # Assign the size of the progress bar to the size of the mineral.
        progress_bar_length: int = mineral_size
        progress_bar_current: int = 0
        progress_bar_line: str = "●"
        progress_bar_slider: str = "◌"
        progress_bar: list = progressBar.filledBar(
            progress_bar_length,
            progress_bar_current,
            15,
            progress_bar_slider,
            progress_bar_line,
        )  # Empty progress bar

        # Creates a list of the chunks to be displayed as a count down.
        chunk_count: list = [
            chunk for chunk in range(mineral_size, 0, -abs(miner.tool.mining_power))
        ]

        await LoadDisplays.display_interaction(
            interaction, miner, mineral_type, DisplayCode.MINING_START
        )
        await asyncio.sleep(0.5)

        for chunk in chunk_count:
            mineral_type.size = chunk  # Updating display of mineral size
            progress_bar_current = chunk
            progress_bar = progressBar.filledBar(
                progress_bar_length,
                progress_bar_current,
                15,
                progress_bar_slider,
                progress_bar_line,
            )
            await LoadDisplays.display_mining_progress(
                interaction, miner, mineral_type, progress_bar[0], DisplayCode.MINING
            )

            # Display gold found
            if random.random() < 0.60:  # 60% chance of gold
                print("DEBUG: adding gold...")
                miner.gold_credits += mineral_gold
                mineral_gold_count += 1

            # Calculate the amount of gold found in mineral.
            miner.gold_found = mineral_gold_count * mineral_gold
            miner.experience += mineral_experience

        # checks if miner can level up and displays level up message.
        if miner.level_up():
            await LoadDisplays.display_miner(interaction, miner, DisplayCode.LEVEL_UP)
            await asyncio.sleep(1)

        # Initiate and display encounter after mining mineral.
        if random.random() < 0.50 and miner.game_over is False:  # 50% chance of enemy
            await LoadDisplays.display_interaction(
                interaction, miner, mineral_type, DisplayCode.MINING_COMPLETE
            )
            enemy_type = PrintMiner.setup_enemy()
            await asyncio.sleep(0.5)

            await LoadDisplays.display_fight(
                interaction, miner, enemy_type, DisplayCode.FIGHT_ENCOUNTER
            )
            print("DEBUG: encounter")
        else:
            await LoadDisplays.display_interaction(
                interaction, miner, mineral_type, DisplayCode.MINING_CONTINUE
            )
            print("DEBUG: continue mine")

    @staticmethod
    async def enemy_attack(
        interaction: discord.Interaction, miner: Miner, enemy: Enemy
    ) -> None:
        """
        Simulates automatic and random turn based fighting between the Miner and an Enemy object.

        Args:
            interaction (discord.Interaction): The Discord interaction triggering the attack.
            miner (Miner): The player character (miner).
            enemy (Enemy): The enemy being attacked.

        Returns:
            None

        Raises:
            None
        """
        enemy.max_health = random.randint(
            enemy.get_lower_bound(enemy.max_health), enemy.max_health
        )
        turn: int = random.randint(0, 1)

        while enemy.max_health > 0 and miner.health > 0:
            print("DEBUG: in fight loop")

            if turn == 0:  # Enemy attack
                enemy.damage = random.randint(
                    enemy.get_lower_bound(enemy.damage), enemy.damage
                )
                miner.lose_health(enemy.damage)

                await asyncio.sleep(1)

                await LoadDisplays.display_fight(
                    interaction, miner, enemy, DisplayCode.FIGHT_ENEMY_ATTACK
                )
                print("DEBUG: enemy turn")
                turn += 1

            elif turn == 1:  # Miner attack
                miner_damage = random.randint(
                    miner.weapon.get_lower_bound(miner.weapon.damage),
                    miner.weapon.damage,
                )
                enemy.lose_health(miner_damage)

                await asyncio.sleep(1)

                await LoadDisplays.display_fight(
                    interaction, miner, enemy, DisplayCode.FIGHT_MINER_ATTACK
                )
                print("DEBUG: player turn")
                turn -= 1

        print("DEBUG: Leave fight loop")
        if enemy.max_health <= 0:
            await asyncio.sleep(1)
            await LoadDisplays.display_fight(
                interaction, miner, enemy, DisplayCode.FIGHT_WIN
            )
            print("DEBUG: player win")

        elif miner.health <= 0:
            await asyncio.sleep(1)
            await LoadDisplays.display_fight(
                interaction, miner, enemy, DisplayCode.FIGHT_LOST
            )
            miner.game_over = True
            print("DEBUG: player lost")

    @staticmethod
    async def miner_flee(
        interaction: discord.Interaction, miner: Miner, enemy: Enemy
    ) -> None:
        """
        Simulates the miner's attempt to flee from an enemy.
        When the miner flees, there is a chance to lose a radom amount of credits.

        Args:
            interaction (discord.Interaction): The Discord interaction triggering the flee action.
            miner (Miner): The player character (miner).
            enemy (Enemy): The enemy from which the miner is fleeing.

        Returns:
            None
        """
        if random.random() < 0.30:  # 30% chance
            lost_credits = random.randint(enemy.gold_credits, enemy.gold_credits * 2)
            miner.lose_credits(lost_credits)
            await LoadDisplays.display_flee(
                interaction, miner, enemy, DisplayCode.FIGHT_FLEE_LOST
            )
            await asyncio.sleep(1)
        else:
            await LoadDisplays.display_flee(
                interaction, miner, enemy, DisplayCode.FIGHT_FLEE_SUCCESS
            )
            await asyncio.sleep(1)
