from emojis import coin
from colors import done, fail, waiting
from nextcord.ext.commands import CommandOnCooldown
from ast import List
from nextcord.ext import commands

import nextcord
import os
import locale
import math
from config import TOKEN
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    print("Bot is ready")
for fn in os.listdir("./cogs"):
    if fn.endswith(".py"):
        bot.load_extension(f"cogs.{fn[:-3]}")
        
bot.run(TOKEN)
