import configparser # the module that parses config.ini and makles it readable
import discord # the actual discord.py wrapper module
from discord.ext import commands # discord commands module
import os # allows you to interact with system files

# initializes and parses the config.ini file so its readable
CONFIG = configparser.ConfigParser() 
CONFIG.read("./config.ini")

# retrieves value(s) from config.ini and assings them to variables
TOKEN = CONFIG.get('Discord', 'Token')
PREFIX = CONFIG.get('Bot', 'Prefix')
# initializes the bot itself, this can be called whatever you want, but in this case "BOT" will be used
BOT = commands.Bot(command_prefix=PREFIX)

# BOT.remove_command('help') # Uncomment this line to remove the help command so you can create your own, which is there by default
# loads the cogs folder, which splits the commands and events into mutliple files
for filename in os.listdir("./src/cogs"): # Lists every file in the cogs directory
    if filename.endswith(".py"): # if the file ends with .py 
        filename = filename[:-3] # remove the last 3 characters from the filename
        BOT.load_extension(f"cogs.{filename}") # loads the extension

BOT.run(TOKEN) # runs the bot with the provided token
