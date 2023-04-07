from nextcord.ext import commands
import nextcord
from colors import done, fail, waiting
from nextcord import Interaction, SlashOption

class G18VN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="error-help", description="Cách sửa lỗi cơ bản")
    async def choose_a_error(
        self,
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

def setup(bot):
    bot.add_cog(G18VN(bot))