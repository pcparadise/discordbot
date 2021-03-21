import configparser 
import discord 
from discord.ext import commands 
import os 

CONFIG = configparser.ConfigParser() 
CONFIG.read("./config.ini")

TOKEN = CONFIG.get('Discord', 'Token')
PREFIX = CONFIG.get('Bot', 'Prefix')

BOT = commands.Bot(command_prefix=PREFIX)

def main():
    # Initialize all the cogs in the cogs folder.
    for filename in os.listdir("./src/cogs"): 
        if filename.endswith(".py"): 
            filename = filename[:-3] 
            BOT.load_extension(f"cogs.{filename}") 

    BOT.run(TOKEN)

main()
