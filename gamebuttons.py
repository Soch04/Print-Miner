"""
Print Miner Discord Bot Game - Game Loader

This Python script contains the code for loading the Print Miner game on Discord. 
It includes the `load_game` function to set up the game 
and the `LoadGameButtons` class to handle the game's interactive buttons.

Author:
    Sonya C

Date updated:
    4/02/2024
"""


from printminer import MenuButtons
import discord

async def load_game(interaction: discord.Interaction):
    embed = discord.Embed(
        title = "Ready to mine?",
    )

    view = LoadGameButtons()
    await interaction.response.send_message(embed = embed, view = view)

class LoadGameButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label = "Start",
                       style = discord.ButtonStyle.success)
    async def start_mine(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer()
        view = MenuButtons()
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
                title = "*mining cancelled*"
            ) ,view = None # removes buttons
        )
