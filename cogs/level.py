from nextcord.ext import commands
import nextcord
import random
from collections import Counter
from pymongo import MongoClient
from cogs.economy import MONGODB_URL
from emojis import coin,ra,rb,rc,rd,rs
from easy_pil import *
class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_database()
        self.economy = self.bot.get_cog('Economy')

    def get_database(self):
        cluster = MongoClient(MONGODB_URL, tlsInsecure=True)
        db = cluster["economy"]
        self.collection = db["users"]
        self.shops_collection = db["shops"]
        return self.collection, self.shops_collection

    async def update_level(self, user, amount):
        collection = self.collection
        query = {"user_id": user.id}
        user_data = collection.find_one(query)
        if user_data is None:
            await self.economy.create_balance(user)
            return
        level = user_data.get("level", {}).get("current", 1)
        exp = user_data.get("level", {}).get("exp", 0)
        maxexp = user_data.get("level", {}).get("nextexp", 10)
        new_exp = exp + amount
        if new_exp >= maxexp:
            level += 1
            new_exp = 0
            maxexp += 10
        collection.update_one(query, {"$set": {"level.current": level, "level.exp": new_exp, "level.nextexp": maxexp}})
        
    @commands.command(name='lv')
    async def lv(self, ctx: commands.Context, member: nextcord.Member = None):
        if not member:
            member = ctx.author
        user_data = await self.economy.get_userdata(member)
        em = nextcord.Embed(title=f"LV")
        level, curexp, nexexp = user_data.get("level", {}).get("current", 0), user_data.get(
            "level", {}).get("exp", 0), user_data.get("level", {}).get("nextexp", 0)
        em.add_field(name="LV", value=f"{level}")
        em.add_field(name="C", value=f"{level}")

        user_datac = {
            "name":f"{member.name}#{member.discriminator}",
            "xp": curexp,
            "level": level,
            "next_level_xp": 100,
            "percentage": curexp,
        }
        background = Editor(Canvas((900, 300), color="#141414"))
        profile_picture = await load_image_async(str(member.avatar.url))
        profile = Editor(profile_picture).resize((150, 150)).rounded_corners(radius=10)
        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)
        card_right_shape = [(600,0), (750,300), (900,300), (900,0)]
        
        background.polygon(card_right_shape,color="#FFFFFF")
        background.paste(profile,(30,30))

        background.rectangle((30, 220), width=650, height=40, color="#FFFFFF", radius=100,)
        background.bar((30,220), max_width=650, height=40,percentage=user_datac["percentage"], color="#282828", radius=40,)

        background.text((200,40), user_datac['name'], font=poppins, color="#FFFFFF")

        background.rectangle((200,100), width=350, height=2, fill="#FFFFFF")
        background.text(
            (200,130),
            f"Level: {user_datac['level']}   XP: {user_datac['xp']}/{user_datac['next_level_xp']}",
            font= poppins_small,
            color="#FFFFFF"
        )
        
        file = nextcord.File(fp=background.image_bytes, filename="levelcard.png")
        await ctx.send(file=file)

    async def get_level(self, user):
        user_data = await self.economy.get_userdata(user)
        level, curexp, nexexp = user_data.get("level", {}).get("current", 0), user_data.get(
            "level", {}).get("exp", 0), user_data.get("level", {}).get("nextexp", 0)
        return level, curexp, nexexp
    
def setup(bot):
    bot.add_cog(Level(bot))
