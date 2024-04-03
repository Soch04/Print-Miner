"""
Print Miner Discord Bot Game - Discord Bot

This Python script contains the code for running the Print Miner game on Discord. 
It includes the `Client` class for setting up the bot, the `print_mine` function for starting the game, 
and the `LoadGameButtons` class for handling the game's interactive buttons.

The script uses the discord.py library to interact with Discord's API and asyncio for asynchronous tasks.
It also uses the dotenv library to load environment variables from a .env file.

Author:
    Sonya C

Date:
    4/02/2024
"""
from typing import Final 
import os
import discord
from dotenv import load_dotenv 
from pathlib import Path
from discord import Client, app_commands
from discord.ext import commands
import gamebuttons

# KEEP TOKEN and GUILD ID SOMEWHERE SAFE
dotenv_path: Path = Path('D:\Files\Code\Python\Print Miner Bot\Discord\.env') #path to .env 
load_dotenv(dotenv_path = dotenv_path) # load the .env file

TOKEN: Final[str] = os.getenv('DISCORD_TOKEN') 
MY_GUILD: Final = discord.Object(id = os.getenv('MY_GUILD'))
print(MY_GUILD)

# BOT SETUP
class Client(discord.Client):
    def  __init__(self,*, intents: discord.Intents):
        super().__init__(intents = intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild = MY_GUILD)
        await self.tree.sync(guild = MY_GUILD) 

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)
bot = commands.Bot(command_prefix = "!", intents = intents)

# EVENTS
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')

@client.tree.command(name = "print-mine", description = "Begin the Print Miner game")
async def print_mine(interaction: discord.Interaction):
    # await interaction.response.send_message(f"{interaction.user.mention} has joined Print Miner!")
    await gamebuttons.load_game(interaction)

# HANDLING THE BOT STARTUP
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# MAIN ENTRY POINT
def main() -> None:
    client.run(token = TOKEN)

if __name__ == '__main__': 
    main()
