from nextcord.ext import commands
import nextcord
# from colors import done, fail, waiting
from nextcord import Interaction, SlashOption
import urllib.request
import os


class G18VN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="pc-error-help", description="Cách sửa lỗi cơ bản")
    async def pc_errors(
        self,
        interaction: nextcord.Interaction,
        Error_Name: int = SlashOption(
            name="error-name",
            description="Chọn loại lỗi bạn đang gặp phải!",
            choices={
                "Lỗi **RPG VX Ace RTP is required to run the game**": 1,
                "Lỗi **__RPGVX RTP is not found__**": 2,
                "Lỗi Failed to load img..../a%%b%%c...x%y%...": 3,
                "Chơi game save xong tắt đi mở lại bị mất hết save": 4,
                "Mở game lên, game hiện khung nhưng màn hình đen/trắng rồi tắt ngay": 5
            }
        ),
    ):

        if Error_Name == 1:
            await interaction.response.send_message("Tải cái này, sau đó cài đặt như thường:\n"
                                                    "https://drive.google.com/file/d/1sUjKqB_zS9ab32PHAjxZ8XvOJ0XJrNiM/view\n"
                                                    "Pass: 1936share.com")
        elif Error_Name == 2:
            await interaction.response.send_message("Tải cái này về, giải nén, cài đặt là xong:\n"
                                                    "https://dl.degica.com/rpgmakerweb/run-time-packages/vx_rtp102e.zip")
        elif Error_Name == 3:
            await interaction.response.send_message("Do locale máy không nhận được tiếng Nhật, đổi locale sang Nhật sẽ khắc phục được lỗi.\n\n"
                                                    "Cách khắc phục:\nĐổi system locale.\n\n"
                                                    "Cách đổi locale:\nhttps://discord.com/channels/692575045603557417/726079992240275487/972890377344385115")
        elif Error_Name == 4:
            await interaction.response.send_message("Giải nén game")
        else:
            await interaction.response.send_message("Hãy thử:\n"
                                                    "- Kiểm tra lại xem máy đã tắt hết windef, firewall, antivirus, ... các phần mềm thứ ba như MSI Afterburner,... (nếu có) chưa -> chưa thì hãy tắt hết\n"
                                                    "- Kiểm tra máy đã đổi locale japan chưa (đa phần các game đều cần)\n"
                                                    "==>> hay gặp nhiều nhất: kiểm tra coi đường dẫn folder có tên nào mình đặt chứa dấu tiếng Việt hay chứa ký tự đặc biệt ko (kiểu / \ , ; . ) -> nếu có hãy đổi về tên bình thường không dấu")

    @nextcord.slash_command(name="joiplay-error-help", description="Cách sửa lỗi cơ bản")
    async def joiplay_errors(
        self,
        interaction: nextcord.Interaction,
        Error_Name: int = SlashOption(
            name="error-name",
            description="Chọn loại lỗi bạn đang gặp phải!",
            choices={
                "Tải joiplay mới nhất": 1,
                "Cách tải RTP VX Ace trên joiplay": 2
            }
        ),

    ):
        if Error_Name == 1:
            await interaction.response.send_message("Download tại đây:\n"
                                                    "https://www.patreon.com/posts/69419140")
        else:
            await interaction.response.send_message("https://cdn.discordapp.com/attachments/726079992240275487/1093214452398178365/km_20230405_1080p_30f_20230405_234034.mp4")

    @nextcord.slash_command(name="kirikiri-error-help", description="Cách sửa lỗi cơ bản")
    async def kirikiri_errors(
        self,
        interaction: nextcord.Interaction,
        Error_Name: int = SlashOption(
            name="error-name",
            description="Chọn loại lỗi bạn đang gặp phải!",
            choices={
                "Tải kirikiroid": 1,
            }
        ),

    ):
        if Error_Name == 1:
            await interaction.response.send_message("Download tại đây:\n"
                                                    "https://androidvisualnovels2.wordpress.com/kirikiroid2/")

    @nextcord.slash_command(name="apk-error-help", description="Cách sửa lỗi cơ bản")
    async def apk_errors(
        self,
        interaction: nextcord.Interaction,
        Error_Name: int = SlashOption(
            name="error-name",
            description="Chọn loại lỗi bạn đang gặp phải!",
            choices={
                "Cài game apk nhưng hiện thông báo `ứng dụng chưa được cài đặt": 1,
            }
        ),

    ):
        if Error_Name == 1:
            await interaction.response.send_message("Ứng dụng chưa đc cài đặt có 6 trường hợp:\n"
                                                    "- máy ko đủ dung lượng (nhớ tính cho đúng và trừ cả dung lượng tự chừa của máy)"
                                                    "- máy chưa có phép cài đặt apk từ ứng dụng ngoài\n"
                                                    "- trong máy đã tồn tại 1 app cùng tên (thường gặp phải khi muốn update ver) -> tức là phải xóa bản cũ đi\n"
                                                    "- apk hỏng -> muốn xác định nó hỏng hay ko phải đi hỏi cả những người khác cài thử, nếu 10 ng bị cả 10 thì đúng là nó hỏng\n"
                                                    "- do bấm apk từ phần download/drive/... chứ ko bấm từ phần apk của \"files của tôi\"\n\n"
                                                    "5 cái trên đều ko bị thì dẫn đến trường hợp 6, vô phương cứu chữa:\n"
                                                    "-> game ko tương thích với máy -> tức là đổi máy đi thì may ra")

    @nextcord.slash_command(name="some-tips", description="Các tips cơ bản cho người mới sử dụng máy tính")
    async def some_tips(
        self,
        interaction: nextcord.Interaction,
        Error_Name: int = SlashOption(
            name="tip-name",
            description="Chọn tip bạn muốn biết",
            choices={
                "Mật khẩu giải nén ở G18VN.com": 1,
                "Đổi locale:": 2,
                "Cách giải nén game nặng": 3,
                "Tải google drive bị lỗi 24h": 4,
                "Tắt windows Defender": 5,
                "Chụp ảnh màn hình máy tính": 6,
                "Download link google drive trên điện thoại": 7,
                "Giải nén game bị ảnh tràn ra bộ sưu tập": 8
            }
        ),
    ):

        if Error_Name == 1:
            await interaction.response.send_message("Mật khẩu là: `g18vn`")
        elif Error_Name == 2:
            await interaction.response.send_message("https://discord.com/channels/692575045603557417/726079992240275487/972890377344385115")
        elif Error_Name == 3:
            await interaction.response.send_message("https://discord.com/channels/692575045603557417/726079992240275487/1088068109388226651")
        elif Error_Name == 4:
            await interaction.response.send_message("https://discord.com/channels/692575045603557417/726079992240275487/977171707301363723")
        elif Error_Name == 5:
            await interaction.response.send_message("https://discord.com/channels/692575045603557417/726079992240275487/1023622569988988988")
        elif Error_Name == 6:
            await interaction.response.send_message("bàn phím văn phòng full size: printscreen ở cụm phím bổ trợ 6 nút bên trên cụm 4 nút định hướng, cạnh cụm phím numpad\n"
                                                    "laptop: fn + print screen hoặc một số máy khác thì chỉ cần ấn print screen, không cần ấn thêm fn\n"
                                                    "laptop cách 2: windows/snipping tool\n"
                                                    "laptop cách 3: shift + windows + S\n"
                                                    "cách 4: download xbox game bar/windows + G/chụp màn hình")
        elif Error_Name == 7:
            await interaction.response.send_message("https://discord.com/channels/692575045603557417/726079992240275487/1085753043120816220")
        else:
            file = nextcord.File("./vhhdpt.png", filename="vhhdpt.png")
            await interaction.response.send_message("Tải `ZArchiver` về , chọn thư mục chứa file game, click vào `Vô hiệu hóa quét đa phương tiện`.\n", file=file)


def setup(bot):
    bot.add_cog(G18VN(bot))
