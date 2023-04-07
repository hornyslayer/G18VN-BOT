from nextcord.ext import commands
import nextcord

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self,ctx):
        await ctx.send('hi!')
def setup(bot):
    bot.add_cog(Ping(bot))