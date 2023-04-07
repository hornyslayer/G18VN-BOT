import asyncio
import datetime
from bs4 import BeautifulSoup
import feedparser
from nextcord.ext import commands
import nextcord
from colors import done, fail, waiting
import sys
from emojis import coin
sys.path.insert(0, '')
class Xoso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bet_data = {}

    def get_latest_item(self):
        feed = feedparser.parse("https://xskt.com.vn/rss-feed/mien-bac-xsmb.rss")
        latest_item = feed.entries[0]
        return latest_item

    def get_info_from_item(self, item):
        description = item["description"]
        title = item["title"]
        info = description.split(":")[1].split()[0]
        return info, title
    
    @commands.command()
    async def xoso(self, ctx):
        latest_item = self.get_latest_item()
        db, title = self.get_info_from_item(latest_item)
        em = nextcord.Embed(
            title=title,
            description=f"ĐB: {db} ",
            color=done
        )
        await ctx.reply(embed=em)

    @commands.command()
    async def bet(self, ctx, number: int, amount):
        economy = self.bot.get_cog('Economy')
        now = datetime.datetime.now()
        target_time = datetime.datetime(now.year, now.month, now.day, 18, 35, 0)
        formatted_time = now.strftime("%d-%m-%Y %H:%M")
        user = ctx.author
        wallet, bank, maxbank = await economy.get_balance(user)
        try:
            amount = int(amount)
        except ValueError:
            pass
        if type(amount) == str:
            if amount.lower() == "max" or amount.lower() == "all":
                amount = int(wallet)
        else:
            amount = int(amount)
            
        if wallet < amount:
            await ctx.reply("Bạn không đủ tiền, hãy thử đặt mức thấp hơn.",delete_after=5)
            return
        elif amount < 0:
            await ctx.reply("Hãy đặt số tiền lớn hơn 0",delete_after=5)
            return
        if number < 0 or number > 99:
            await ctx.reply("Số không hợp lệ, hãy đặt trong khoảng từ `00-99`",delete_after=5)
            return
        if now.time() >= datetime.time(18, 15) and now.time() <= datetime.time(18, 25):
            await ctx.reply("Không thể đặt cược trong khoảng thời gian này, hãy thử lại sau",delete_after=5)
            return
        await economy.update_wallet(user, -amount)
        em = nextcord.Embed(title="Vé LOTTE")
        em.add_field(name="Số đã mua", value=number, inline=True)
        em.add_field(name="Số tiền", value=economy.format_money(amount), inline=True)
        em.add_field(name="Thời gian trả", value= formatted_time, inline=True)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

        async def get_result():
            await asyncio.sleep((target_time - now).total_seconds())
            latest_item = self.get_latest_item()
            db, title = self.get_info_from_item(latest_item)
            result = int(db[-2:])
            if number == result:
                win_amount = int(amount * 70)
                await economy.update_wallet(user, win_amount)
                em = nextcord.Embed(title="KẾT QUẢ LOTTE",description=f"Kết quả là: `{db}`\nChúc mừng bạn đã trúng số! Bạn được nhận {economy.format_money(win_amount)} {coin}")
                await ctx.reply(embed=em)
            else:
                em = nextcord.Embed(title="KẾT QUẢ LOTTE",description=f"Kết quả là: `{db}`\nRất tiếc, bạn không trúng số. Cố gắng thêm lần sau nhé!")
                await ctx.reply(embed=em)
        asyncio.create_task(get_result())

def setup(bot):
    bot.add_cog(Xoso(bot))
