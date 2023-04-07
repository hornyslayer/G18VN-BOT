from emojis import coin
from colors import done, fail, waiting
from nextcord.ext.commands import CommandOnCooldown
from ast import List
from nextcord import Interaction, SlashOption
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


@bot.slash_command(name="error-help", description="Cách sửa lỗi cơ bản")
async def choose_a_error(
    interaction: nextcord.Interaction,
    Platform_Name: str = SlashOption(
        name="platform-name",
        description="Nền tảng bạn đang chơi!",
        choices={
            "Joiplay": "joiplay",
            "PC": "PC",
            "Android": "Android"
        },
    ),

    Error_Name: str = SlashOption(
        name="error-name",
        description="Chọn loại lỗi bạn đang gặp phải!",
        choices={
            "RTP VXAce": "Cài đặt RTP VXAce",
            "Font chữ bị lỗi": "Đổi locale, cài font tương ứng"
        }
    )

):
    await interaction.response.send_message(f"{Error_Name}")


bot.run(TOKEN)
