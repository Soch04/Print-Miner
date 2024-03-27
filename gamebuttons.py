"""
Print Miner Discord Bot Game - Game Loader

This Python script contains the code for loading the Print Miner game on Discord. 
It includes the `load_game` function to set up the game and the `LoadGameButtons` class to handle the game's interactive buttons.

The script uses the discord.py library to interact with Discord's API and asyncio for asynchronous tasks.

Author:
    Sonya C

Date:
    2/26/2024
"""


import discord
from printminer import LoadButtons, PrintMiner

async def load_game(interaction: discord.Interaction):
    miner = PrintMiner.setup_miner()
    embed = discord.Embed(
        title = "Ready to mine?",
    )

    view = LoadGameButtons(miner)
    await interaction.response.send_message(embed = embed, view = view)

class LoadGameButtons(discord.ui.View):
    def __init__(self,miner):
        super().__init__(timeout = None)
        self.miner = miner

    @discord.ui.button(label = "Start",
                       style = discord.ButtonStyle.success)
    async def start_mine(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer()
        view = LoadButtons(self.miner)
        await interaction.edit_original_response(
            embed = discord.Embed(
                title = "Welcome!"
            ) ,view = view 
        )

    @discord.ui.button(label = "Cancel",
                       style = discord.ButtonStyle.red)
    async def cancel_mine(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.edit_original_response(
            embed = discord.Embed(
                title = "mining cancelled"
            ) ,view = None # removes buttons
        )

