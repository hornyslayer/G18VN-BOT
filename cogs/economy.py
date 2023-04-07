from ast import List
from nextcord.ext import commands
import nextcord
import os
import locale
import math
from pymongo import MongoClient
from colors import done, fail, waiting
import asyncio
import aiosqlite
import random
from colors import done, fail, waiting
from emojis import coin, a, b, c, d, e, f, g, h, slots
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '')

MONGODB_URL = 'mongodb+srv://admin:18810410139Aa.@cluster0.iltqw84.mongodb.net/?retryWrites=true&w=majority'

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_coins = {}
        self.get_database()
    def get_database(self): 
        cluster = MongoClient(MONGODB_URL, tlsInsecure=True)
        db = cluster["economy"]
        self.collection = db["users"]
        print(db)
        return self.collection
    @commands.Cog.listener()
    async def on_ready(self):
        commands.db = await aiosqlite.connect("bank.db")
        await asyncio.sleep(3)
        async with commands.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS inv (name TEXT, id TEXT, desc TEXT, amount INTEGER, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS shop (name TEXT, id TEXT, desc TEXT, cost INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS level (level INTEGER, exp FLOAT, maxexp FLOAT, user INTEGER)")
        await commands.db.commit()

    @commands.Cog.listener()
    async def on_message(self, ctx):
        user = ctx.author
        if user.bot:
            return
        now = datetime.now()  # lấy thời gian hiện tại
        last_coins_time = self.last_coins.get(user.id)
        if last_coins_time is None or now - last_coins_time > timedelta(seconds=60):
            reward = random.randint(5, 100)
           # await self.update_wallet(user, reward)
            # cập nhật thời gian cuối cùng người dùng nhận tiền
            self.last_coins[user.id] = now
            #print(f"{user} nhận được {reward} vàng")

    def format_money(self, amount):
        # cập nhật locale theo ngôn ngữ máy tính
        locale.setlocale(locale.LC_ALL, '')
        return locale.format_string("%d", amount, grouping=True)

    async def create_inv(self, user):
        async with commands.db.cursor() as cursor:
            await cursor.execute("INSERT INTO inv VALUES (?, ?, ?, ?, ?)", (None, None, None, None, user.id)) #Thêm item có id = 1 vào inventory với số lượng bằng 0.
        await commands.db.commit()
        return
    

    async def get_inv(self, user):
        async with commands.db.cursor() as cursor:
            await cursor.execute("SELECT shop.name, inv.amount FROM shop INNER JOIN inv ON shop.id = inv.id WHERE inv.user = ? AND inv.amount > 0", (user.id,))
            data = await cursor.fetchall()
            if data is None:
                await self.create_inv(user)
                return 0, 0, 0
            inventory = {row[0]: row[1] for row in data}
            return inventory

    async def update_shop(self, name: str, id: str, desc: str, cost: int):
        async with commands.db.cursor()as cursor:
            await cursor.execute("INSERT INTO shop VALUES(?, ?, ?, ?)", (name, id, desc, cost))
        await commands.db.commit()
        return

    async def update_maxbank(self, user, amount: int):
        collection = self.collection
        query = {"user_id": user.id}
        update = {"$inc": {"maxbank": amount}}
        result = collection.update_one(query, update)
        if result.modified_count == 0:
            await self.create_balance(user)
            return 0
        return result.modified_count

    async def create_balance(self, user):
        collection = self.collection
        query = {"user_id": user.id}
        if collection.count_documents(query) == 0: # If a user is not in the database, adds the user to the db
            new_bank_account = {"wallet": 0,
                                "bank": 100,
                                "maxbank": 100000,
                                "user_id": user.id
                                }
            collection.insert_one(new_bank_account)
            request = new_bank_account
        else: # If a user is in the database, returns the user json file
            request = collection.find_one(query)
        self.user_data = request
        return self.user_data


    async def get_balance(self, user):
        collection = self.collection
        query = {"user_id": user.id}
        user_data = collection.find_one(query)
        if user_data is None:
            user_data = await self.create_balance(user)
        wallet, bank, maxbank = user_data.get("wallet", 0), user_data.get("bank", 100), user_data.get("maxbank", 100000)
        return wallet, bank, maxbank

    async def update_wallet(self, user, amount: int):
        collection = self.collection
        query = {"user_id": user.id}
        user_data = collection.find_one(query)
        if user_data is None:
            await self.create_balance(user)
            return 0
        wallet = user_data.get("wallet", 0)
        new_wallet = wallet + amount
        collection.update_one(query, {"$set": {"wallet": new_wallet}})
        return new_wallet


    async def update_bank(self, user, amount: int):
        collection = self.collection
        user_data = collection.find_one({"user_id": user.id})
        if user_data is None:
            await self.create_balance(user)
            return 0
        wallet, bank, maxbank = user_data.get("wallet", 0), user_data.get("bank", 100), user_data.get("maxbank", 100000)
        capacity = int(maxbank - bank)
        if amount > capacity:
            await self.update_wallet(user, amount)
            return 1
        collection.update_one({"user_id": user.id}, {"$inc": {"bank": amount}})


    @commands.command(name='balance')
    async def balance(self, ctx: commands.Context, member: nextcord.Member = None):
        if not member:
            member = ctx.author
        wallet, bank, maxbank = await self.get_balance(member)
        em = nextcord.Embed(title=f"---G18VN BANK---")
        em.add_field(name=":money_with_wings: Tiền mặt:",
                     value=self.format_money(wallet))
        em.add_field(name=":bank: Ngân hàng:",
                     value=f"{self.format_money(bank)}/{self.format_money(maxbank)}")
        em.add_field(name=":moneybag: Tổng tài sản:",
                     value=f"{self.format_money(wallet+bank)}")
        if member:
            em.set_author(name=member, icon_url=member.avatar.url)
        else:
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=em)

    @commands.command(name='bal')
    async def bal_cmd(
        self, ctx, member: nextcord.Member = None): await self.balance(ctx, member)

    @commands.command(name='withdraw')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def withdraw(self, ctx: commands.Context, amount):
        wallet, bank, maxbank = await self.get_balance(ctx.author)
        try:
            amount = int(amount)
        except ValueError:
            pass
        if type(amount) == str:
            if amount.lower() == "max" or amount.lower() == "all":
                amount = int(bank)
        else:
            amount = int(amount)
        if (amount > bank):
            return await ctx.reply("Bạn không đủ tiền trong ngân hàng")
        elif (amount < 0):
            return await ctx.reply("Số tiền rút phải lớn hơn 0")

        bank_res = await self.update_bank(ctx.author, -amount)
        wallet_res = await self.update_wallet(ctx.author, amount)
        if bank_res == 1:
            return await ctx.send("Oong beo 2")
        em = nextcord.Embed(
            description=f":white_check_mark: Rút thành công **{self.format_money(amount)}** {coin} về ví", color=done)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='with')
    async def with_cmd(self, ctx, amount):
        await self.withdraw(ctx, amount)

    @commands.command(name='deposit')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deposit(self, ctx: commands.Context, amount):
        wallet, bank, maxbank = await self.get_balance(ctx.author)
        try:
            amount = int(amount)
        except ValueError:
            pass
        if type(amount) == str:
            if amount.lower() == "max" or amount.lower() == "all":
                amount = int(wallet)
        else:
            amount = int(amount)
        if (amount < 0):
            return await ctx.reply("Số tiền gửi phải lớn hơn 0")
        bank_res = await self.update_bank(ctx.author, amount)
        wallet_res = await self.update_wallet(ctx.author, -amount)
        if bank_res == 1:
            return await ctx.send("Oong beo 2")
        em = nextcord.Embed(
            description=f":white_check_mark: Gửi thành công **{self.format_money(amount)}** {coin} vào ngân hàng.", color=done)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='dep')
    async def dep_cmd(self, ctx, amount): await self.deposit(ctx, amount)

    @commands.command(name='give')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def give(self, ctx: commands.Context, member: nextcord.Member, amount):
        wallet, bank, maxbank = await self.get_balance(ctx.author)
        try:
            amount = int(amount)
        except ValueError:
            pass
        if type(amount) == str:
            if amount.lower() == "max" or amount.lower() == "all":
                amount = int(wallet)
        else:
            amount = int(amount)
        if amount > wallet:
            await ctx.reply("Bạn không đủ tiền để gửi")
        elif amount < 0:
            await ctx.reply("Hãy nhập số lớn hơn 0")
        wallet_res = await self.update_wallet(ctx.author, -amount)
        wallet_res2 = await self.update_wallet(member, amount)
        if wallet_res2 == 0:
            await self.create_balance(member)
            await self.update_wallet(member, amount)
        elif wallet_res == 0:
            await self.create_balance(ctx.author)
            await self.update_wallet(ctx.author, -amount)
        em = nextcord.Embed(
            description=f":white_check_mark: {member.name} đã nhận **{self.format_money(amount)}** {coin}", color=done)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='rob')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rob(self, ctx: commands.Context, member: nextcord.Member):
        if random.random() < 0.7:
            wallet, bank, maxbank = await self.get_balance(ctx.author)
            fail_amount = wallet*0.7
            em = nextcord.Embed(
                description=f":x: {ctx.author} không thành công khi cố gắng trộm {member.name} và bị phạt {self.format_money(fail_amount)} {coin}", color=fail)
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            self.update_wallet(ctx.author, -1000)
            await ctx.reply(embed=em)
            return
        wallet2, bank2, maxbank2 = await self.get_balance(member)
        rob_amount = 0.7 * wallet2
        wallet_res = await self.update_wallet(ctx.author, rob_amount)
        wallet_res2 = await self.update_wallet(member, -rob_amount)
        if wallet_res2 == 0:
            await self.create_balance(member)
            await self.update_wallet(member, -rob_amount)
        elif wallet_res == 0:
            await self.create_balance(ctx.author)
            await self.update_wallet(ctx.author, rob_amount)
        em = nextcord.Embed(
            description=f":white_check_mark: {member.name} đã bị {ctx.author} trộm mất **{self.format_money(rob_amount)}** {coin}", color=done)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='work')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def work(self, ctx: commands.Context):
        amount = random.randint(10, 1000)
        await self.update_wallet(ctx.author, amount)
        descriptions = [
            "Bạn vừa giặt đồ thuê",
            "Bạn vừa giúp người hàng xóm chăm sóc vườn cây",
            "Bạn vừa làm thêm tại cửa hàng quần áo",
            "Bạn vừa đi giúp người hàng xóm chăm sóc thú cưng",
            "Bạn vừa làm thêm tại quán ăn"
        ]
        description = random.choice(descriptions)
        em = nextcord.Embed(
            description=f":white_check_mark: {description} và kiếm được **{self.format_money(amount)}** {coin}", color=0x2ecc71)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='slut')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def slut(self, ctx: commands.Context):
        amount = random.randint(100, 2000)
        await self.update_wallet(ctx.author, amount)
        descriptions = [
            "Bạn đi làm gái!",
            "Bạn đi làm cave đực!"
        ]
        description = random.choice(descriptions)
        em = nextcord.Embed(
            description=f":white_check_mark: {description} và kiếm được **{self.format_money(amount)}** {coin}", color=0x2ecc71)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='crime')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def crime(self, ctx: commands.Context):
        amount = random.randint(100, 10000)
        if random.random() < 0.5:
            fail_amount = amount/2
            await self.update_wallet(ctx.author, -fail_amount)
            description = f"Bạn bị bắt và bị phạt {self.format_money(fail_amount)}"
            color = 0xe74c3c
        else:
            descriptions = [
                f"Bạn đã trộm được {self.format_money(amount)}",
                f"Bạn đã lấy được một món quà từ người nào đó và bán được {self.format_money(amount)}",
                f"Bạn đã tỏ ra là một tên trộm thực thụ, khi trộm được",
                f"Bạn đang trở nên khá tài năng về việc ăn trộm, khi kiếm được {self.format_money(amount)}",
                f"Bạn đã trộm đồ của viett và bán được {self.format_money(amount)}"
            ]
            description = random.choice(descriptions)
            color = 0x2ecc71
        em = nextcord.Embed(description=f"{description} {coin}", color=color)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='daily')
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        amount = random.randint(100, 1000)
        await self.update_wallet(ctx.author, amount)
        em = nextcord.Embed(
            description=f":white_check_mark: Điểm danh ngày thành công bạn nhận được **{self.format_money(amount)}** {coin}", color=done)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name='weekly')
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def weekly(self, ctx: commands.Context):
        amount = random.randint(1000, 10000)
        await self.update_wallet(ctx.author, amount)
        em = nextcord.Embed(
            description=f":white_check_mark: Điểm danh tuần thành công bạn nhận được **{self.format_money(amount)}** {coin}", color=done)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=em)
    # Coin Flip

    @commands.command(name='coinflip')
    async def coinflip(self, ctx, choice, amount):
        wallet, bank, maxbank = await self.get_balance(ctx.author)
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
            await ctx.reply("Bạn không đủ tiền, hãy thử đặt mức thấp hơn.")
            return
        elif amount < 0:
            await ctx.reply("Hãy đặt số tiền lớn hơn 0")
            return
        side = random.choice(["Head", "Tail"])
        em = nextcord.Embed(
            title=f"{ctx.author}", description=f"Tung đồng xu...", color=waiting)
        msg = await ctx.reply(embed=em)
        await asyncio.sleep(2)
        if side.lower() == choice.lower():
            await self.update_wallet(ctx.author, amount*2)
            em = nextcord.Embed(
                title=f"{side}", description=f"Bạn đã đoán đúng! Bạn nhận được **{self.format_money(amount*2)}** {coin}", color=done)
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            await msg.edit(embed=em)
        else:
            await self.update_wallet(ctx.author, -amount)
            em = nextcord.Embed(
                title=f"{side}", description=f"Rất tiếc, bạn đã đoán sai. Bạn mất **{self.format_money(amount)}** {coin}", color=fail)
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            await msg.edit(embed=em)

    @commands.command(name='cf')
    async def coinflip_cmd(self, ctx, choice, amount): await self.coinflip(
        ctx, choice, amount)

    @commands.command(name='slots')
    async def slots(self, ctx, amount):
        user = ctx.author
        wallet, bank, maxbank = await self.get_balance(ctx.author)
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
            msg = await ctx.reply("Bạn không đủ tiền, hãy thử đặt mức thấp hơn.")
            await msg.delete(delay=5)
            return
        elif amount < 0:
            msg = await ctx.reply("Hãy đặt số tiền lớn hơn 0")
            await msg.delete(delay=5)
            return
        slot1 = [a, b, c, d, e, f, g]
        slot2 = [a, b, c, d, e, f, g]
        slot3 = [a, b, c, d, e, f, g]
        random_sample1 = random.sample(slot1, k=3)
        random_sample2 = random.sample(slot2, k=3)
        random_sample3 = random.sample(slot3, k=3)

        sep = "   :   "
        des = (f"**[ {slots}: l SLOTS  ]**\n"
               f"**------------------**\n"
               f"{sep.join(random_sample1)}\n"
               f"{sep.join(random_sample2)}   📍\n"
               f"{sep.join(random_sample3)}\n"
               f"**------------------**"
               )
        msg = await ctx.reply(des)
        for i in range(5):
            await asyncio.sleep(0.2)
            total = len(slot1)
            if total % 2 == 0:  # if even
                mid = total / 2
            else:
                mid = (total + 1) // 2

            random.shuffle(slot1)
            random.shuffle(slot2)
            random.shuffle(slot3)
            next: List[List[str]] = []
            for x in range(total):
                next.append([slot1[x], slot2[x], slot3[x]])
            des = (f"**Bạn đã đặt cược ``{self.format_money(amount)}`` {coin} **\n"
                   f"**[  {slots} l SLOTS  ]**\n"
                   f"**------------------**\n"
                   f"{sep.join(next[mid - 1])}\n"
                   f"{sep.join(next[mid])}   📍\n"
                   f"{sep.join(next[mid + 1])}\n"
                   f"**------------------**"
                   )
            await msg.edit(des)

        result: List[List[str]] = []
        for x in range(total):
            result.append([slot1[x], slot2[x], slot3[x]])
        des_re = (f"**Bạn đã đặt cược ``{self.format_money(amount)}`` {coin} \n"
                  f"**[  {slots} l SLOTS  ]**\n"
                  f"**------------------**\n"
                  f"{sep.join(result[mid - 1])}\n"
                  f"{sep.join(result[mid])}   📍\n"
                  f"{sep.join(result[mid + 1])}\n"
                  f"**------------------**"
                  )
        slot = result[mid]
        s1 = slot[0]
        s2 = slot[1]
        s3 = slot[2]
        des_result = "WIN"
        des_result2 = "WIN"
        if s1 == s2 == s3:
            reward = round(amount / 2)
            des_result = f"**BIG WIN**"
            des_result2 = f"**Bạn đặt cược {amount} và thắng được {reward}**"
            await self.update_bank(user, +reward)
        elif s1 == s2 or s2 == s3 or s1 == s3:
            reward = round(amount / 4)
            des_result = f"**WIN**"
            des_result2 = f"**Bạn đặt cược {amount} và thắng được {reward}**"
            await self.update_bank(user, +reward)
        else:
            await self.update_bank(user, -amount)
            des_result = f"**LOSE**"
            des_result2 = f"**Bạn đặt cược {amount} và thua sạch**"
        des = (f"{des_re}\n"
               f"**| : : :  {des_result}  : : : |**\n"
               f"**{des_result2}**")
        return await msg.edit(des)

    @commands.command(name='sl')
    async def slots_cmd(self, ctx, amount): await self.slots(ctx, amount)

    @commands.command()
    @commands.is_owner()
    async def add_items(self, ctx, name: str, id: str, desc: str, cost: int):
        await self.update_shop(name, id, desc, cost)
        await ctx.send("Item added!", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx):
        embed = nextcord.Embed(title="G18VN SHOP")
        async with commands.db.cursor() as cursor:
            await cursor.execute("SELECT name, desc, cost FROM shop")
            shop = await cursor.fetchall()
            for item in shop:
                embed.add_field(
                    name=item[0], value=f"{item[1]} | Cost: {item[2]}", inline=False)
        await ctx.send(embed=embed, view=ShopView(commands))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def inventory(self, ctx):
        inventory = await self.get_inv(ctx.author)
        if not inventory:
            await ctx.send("Bạn không có bất kỳ mặt hàng nào trong túi đồ của mình!")
            return
        embed = nextcord.Embed(title="Túi đồ của bạn")
        for item, amount in inventory.items():
            embed.add_field(
                name=item, value=f"Số lượng: {amount}", inline=False)
        await ctx.send(embed=embed)


class ShopView(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.bot = bot

    @nextcord.ui.button(
        label="Laptop", style=nextcord.ButtonStyle.blurple, custom_id="laptop"
    )
    async def laptop(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT laptop from inv WHERE user = ?", (interaction.user.id,))
            item = await cursor.fetchone()
            if item is None:
                await cursor.execute("INSERT INTO inv VALUES(?, ?, ?, ?)", (1, 0, 0, interaction.user.id))
            else:
                await cursor.execute("UPDATE inv SET laptop = ? WHERE user = ?", (item[0]+1, interaction.user.id))
        await self.bot.db.comit()
        await interaction.send("Đã mua thành công laptop")


def setup(bot):
    bot.add_cog(Economy(bot))
