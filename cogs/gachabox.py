import random
from nextcord.ext import commands
import nextcord

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = {
            "item1": {"name": "Item 1", "quality": "D", "value": 10},
            "item2": {"name": "Item 2", "quality": "C", "value": 20},
            "item3": {"name": "Item 3", "quality": "B", "value": 30},
            "item4": {"name": "Item 4", "quality": "A", "value": 50},
            "item5": {"name": "Item 5", "quality": "S", "value": 80},
            "item6": {"name": "Item 6", "quality": "SS", "value": 120},
            "item7": {"name": "Item 7", "quality": "SSS", "value": 200}
        }

    @commands.command(name="gacha")
    async def gacha(self, ctx):
        item = random.choice(list(self.items.values()))
        message = f"You got **{item['quality']}** quality {item['name']}! It's worth {item['value']} coins."
        await ctx.send(message)
        
def setup(bot):
    bot.add_cog(Ping(bot))