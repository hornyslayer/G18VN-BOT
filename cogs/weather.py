import nextcord
import requests
from nextcord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def weather(self, ctx, *, city: str):
        ICON_BASE_URL = 'http://openweathermap.org/img/wn/'
        api_key = 'e4d4e335f0fc0f7d488bd7ecf5a2f3f7'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=vi'
        response = requests.get(url)
        data = response.json()
        if 'main' in data:
            city = data['sys']['country']
            name = data['name']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            weather_description = data['weather'][0]['description']
            weather_icon = data['weather'][0]['icon']
            icon_url = f'{ICON_BASE_URL}{weather_icon}@2x.png'
            message = (f'Thời tiết tại **{name}** đang có nhiệt độ là **{temperature}°C**'
                       f'\n {weather_description}.\nCảm giác như **{feels_like}°C**\n Độ ẩm **{humidity}%**.')
            
        else:
            message = f'Xin lỗi tôi không tìm thấy thành pố {city}. hãy thử lại.'

        # Tạo embed
        embed = nextcord.Embed(title=f'Thời tiết ở {name}', description=message, color=0x00ff00)
        embed.add_field(name="Quốc gia", value=city, inline=False)
        embed.set_thumbnail(url=icon_url)

        # Gửi embed
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Weather(bot))  