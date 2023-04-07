from nextcord.ext import commands
import nextcord
from colors import done, fail, waiting

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self,ctx):
        em = nextcord.Embed(title = "Tổng hợp lệnh",
                            description=("`!help` Hiển thị toàn bộ lệnh\n"
                                         "`!weather` Xem thời tiết\n"
                                         "`!work` Làm việc kiếm tiền\n"
                                         "`!crime` Đi làm ăn trộm\n"
                                         "`!slut` Đi làm 4\n"
                                         "`!rob` Trộm tiền của người khác\n"
                                         "`!balance` Kiểm tra tài khoản\n"
                                         "`!withdraw` Rút tiền về ví\n"
                                         "`!deposit` Gửi tiền vào ngân hàng\n"
                                         "`!give` Gửi tiền cho người khác\n"
                                         "`!coinflip` head || tail Chơi trò chơi coinflip\n"
                                         "`!fish` Tham gia câu cá\n"
                                         "`!slots` Chơi trò chơi slots\n"
                                         "`!poll` Bỏ phiếu cú pháp `poll title; Description; choice, choice2, choice3, choice4, choice5: time (minute)`")
                            ,color=done)
        await ctx.reply(embed=em)

def setup(bot):
    bot.add_cog(Help(bot))