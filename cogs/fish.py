from nextcord.ext import commands
import nextcord
import random
from collections import Counter
from emojis import coin,ra,rb,rc,rd,rs
import aiosqlite

class Fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_level(self, user, amount):
        async with commands.db.cursor() as cursor:
            await cursor.execute("SELECT exp FROM level WHERE user = ?", (user.id,))
            data = await cursor.fetchone()
            if data is None:
                await self.create_level(user)
                return 0
            await cursor.execute("UPDATE level SET exp = exp + ? WHERE user = ?", (amount, user.id))
            level, exp, maxexp = await self.get_level(user)
            if exp >= maxexp:
                level+=1
                await cursor.execute("UPDATE level SET level = ? WHERE user = ?", (level, user.id))
                await cursor.execute("UPDATE level SET exp = ? WHERE user = ?", (0, user.id))
                await cursor.execute("UPDATE level SET maxexp = ? WHERE user = ?", (maxexp + 10, user.id))
        await commands.db.commit()

    async def get_level(self, user):
        async with commands.db.cursor() as cursor:
            await cursor.execute("SELECT level, exp, maxexp FROM level WHERE user = ?", (user.id,))
            data = await cursor.fetchone()
            if data is None:
                await self.create_level(user)
                return 1, 10, 100
            level, exp, maxexp = data[0], data[1], data[2]
        return level, exp, maxexp
    async def create_level(self, user):
        async with commands.db.cursor() as cursor:
            await cursor.execute("INSERT INTO level VALUES(?, ?, ?, ?)", (1, 10, 100, user.id))
        await commands.db.commit()
        return
    @commands.command(name='lv')
    async def lv(self,ctx: commands.Context, member: nextcord.Member = None):
        if not member:
            member = ctx.author
        level, exp, maxexp = await self.get_level(member)
        em = nextcord.Embed(title=f"LV")
        em.add_field(name="exp", value = f"{level} {exp} {maxexp}")
        if member:
            em.set_author(name=member, icon_url=member.avatar.url)
        else:
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=em)  
    @commands.command()
    async def fish(self, ctx):
        economy = self.bot.get_cog('Economy')
        fish_list = {
            '💿': {'rarity': [rd, rc, rb, ra, rs], 'price': [1, 2, 10, 20, 50]},
            '🧦': {'rarity': [rd, rc, rb, ra, rs], 'price': [2, 4, 15, 30, 100]},
            '🐟': {'rarity': [rd, rc, rb, ra, rs], 'price': [10, 50, 100, 500, 1000]},
            '🦞': {'rarity': [rd, rc, rb, ra, rs], 'price': [20, 60, 150, 500, 1000]},
            '🦐': {'rarity': [rd, rc, rb, ra, rs], 'price': [20, 95, 200, 500, 1500]},
            '🐡': {'rarity': [rd, rc, rb, ra, rs], 'price': [31, 120, 300, 600, 1600]},
            '🐠': {'rarity': [rd, rc, rb, ra, rs], 'price': [50, 200, 500, 1000, 3000]},
        }
        
        fish_counts = random.choices(range(6), weights=[0, 50, 40, 15, 4, 1], k=1)[0]
        fish_names = []
        fish_prices_list = []
        level, exp, maxexp = await self.get_level(ctx.author)
        for i in range(fish_counts):
            fish = random.choices(list(fish_list.keys()), weights=[5,6, 50, 20, 15, 4, 1], k=1)[0]
            rarity_index = random.choices(range(len(fish_list[fish]['rarity'])), weights=calculate_weights(level), k=1)[0]
            fish_rarity = fish_list[fish]['rarity'][rarity_index]
            fish_price = fish_list[fish]['price'][rarity_index]
            fish_names.append(f"{fish} ({fish_rarity})")
            fish_prices_list.append(fish_price)
        
        if fish_counts == 0:
            await ctx.send("Bạn không câu được gì cả!")
        else:
            exp_points = fish_counts * (rarity_index + 1 ) + level
            fish_count_dict = Counter(fish_names)
            fish_list_str = "\n".join([f"{name} x **{fish_count_dict[name]}** `{fish_prices_list[i] * fish_count_dict[name]}` {coin}" for i, name in enumerate(fish_count_dict)])
            fish_prices_sum = sum([fish_prices_list[i] * fish_count_dict[name] for i, name in enumerate(fish_count_dict)])
            em = nextcord.Embed(description=(f"**Bạn câu được `{fish_counts}` cá**\n"
                                             f"**-----------------------**\n"
                                             f"{fish_list_str}\n"
                                             f"**-----------------------**\n"
                                             f"Bán được `{fish_prices_sum}` {coin} và `{exp_points}` EXP\n"
                                             ),color=0x00e1ff)
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            await economy.update_wallet(ctx.author, fish_prices_sum)
            await self.update_level(ctx.author, exp_points)
            await ctx.send(embed=em, delete_after=30)
            
def calculate_weights(level):
    weights_0 = max(50 - level * 2, 0)
    weights_1 = max(20 - level * 1, 0)
    weights_3 = min(level * 2 + 10, 50)
    weights_4 = min(level * 2 + 5, 25)
    weights = [weights_0, weights_1, 15, weights_3, weights_4]
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    #print(normalized_weights)
    return normalized_weights
def setup(bot):
    bot.add_cog(Fish(bot))
