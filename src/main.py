import configparser 
import discord 
from discord.ext import commands 

CONFIG = configparser.ConfigParser() 
CONFIG.read("./config.ini")

TOKEN = CONFIG.get('Discord', 'Token')
PREFIX = CONFIG.get('Bot', 'Prefix')

BOT = commands.Bot(command_prefix=PREFIX)

# add your module name here once completed 
MODULES = ["exampleCommandModule", "exampleEventModule"]

def main():
    for module in MODULES:
        BOT.load_extension(f"cogs.{module}")
    BOT.run(TOKEN)

main()
