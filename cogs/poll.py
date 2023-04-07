import nextcord
from nextcord.ext import commands, tasks
from emojis import POLL_OPTION_EMOJIS
import datetime as dt

class Poll(commands.Cog):
    SENT_MESSAGE_IDS = []
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_message(self, message):
        global POLL_OPTION_EMOJIS
        if message.content.startswith("!poll"):
            # Extract the parameters from the command
            params = message.content.split(";")
            question = params[0].replace("!poll","").strip()
            options = [x.strip() for x in params[1].strip().split(",")]
            orig_options = options
            options_count = len(options)
            countdown = params[2]

            try:
                countdown = int(countdown)
            except Exception as e:
                pass
            
            # validate parameters to check if there are any errors
            error = self.validate_params(question, options, countdown)

            if error is not None:
                # If parameters are not in the expected format, send error message
                embed = nextcord.Embed(title="Error", description=error, color=nextcord.Color.red())
                sent = await message.channel.send(embed=embed)
                return

            # If there is no error, send the poll message
            for i in range(len(options)):
                options[i] = f"{POLL_OPTION_EMOJIS[i]} {options[i]}"
            options = '\n'.join(options)
            embed = nextcord.Embed(title=f"Bỏ phiếu tạo bởi {message.author}", description=f"**{question}**\n{options}\n", color=0x12ff51)
            sent = await message.channel.send(embed=embed)

            POLL_OPTION_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            for i in range(options_count):
                # React with the allowed set of emojis
                await sent.add_reaction(POLL_OPTION_EMOJIS[i])
            
            # Add sent message id to a global list
            self.SENT_MESSAGE_IDS.append(sent.id)
            end_time = dt.datetime.utcnow() + dt.timedelta(seconds=int(countdown)*60)

            # define the background task to update the countdown message
            @tasks.loop(seconds=1)
            async def update_countdown():
                # Calculate remaining time in countdown
                remaining_time = (end_time - dt.datetime.utcnow()).total_seconds()

                if remaining_time > 0:
                    # If countdown still didn't expire
                    minutes, seconds = divmod(int(remaining_time), 60)

                    # Edit the message
                    description = f"**{question}**\n{options}\n\n*Bỏ phiếu kết thúc sau {minutes:02d}:{seconds:02d}*"
                    embed = nextcord.Embed(title=f"Bỏ phiếu tạo bởi {message.author}", description=description, color=0x12ff51)
                    await sent.edit(embed=embed)

                else:
                    sent_message = await message.channel.fetch_message(sent.id)

                    poll_results_count = {}
                    total_reactions = 0

                    # If countdown expired
                    for reaction in sent_message.reactions:
                        # Enumerate message reactions
                        for ind, emoji in enumerate(POLL_OPTION_EMOJIS):
                            # Count number of times an emoji
                            if str(reaction.emoji) == emoji:
                                poll_results_count[ind+1] = reaction.count - 1
                                if reaction.count>1:
                                    # Also calculate the total reactions
                                    total_reactions+=1

                    # Craft the results message
                    poll_results_message = ""
                    for ind, count in enumerate(poll_results_count):
                        # Calculate percentage value of each option                  
                        if total_reactions == 0:
                            perc = 0
                        else:
                            perc = round(poll_results_count[ind+1]/total_reactions * 100)
                        poll_results_message+=f"{orig_options[ind]} ~ {perc}% ({poll_results_count[ind+1]} votes)\n"
                    
                    # Send the results message
                    embed = nextcord.Embed(title=f"Kết quả bỏ phiếu: {question}", description=f"Bỏ phiếu tạo bởi {message.author}\n({poll_results_message})", color=0x13a6f0)
                    await message.channel.send(embed=embed)
                    # Delete the original poll message and end tasks.loop function
                    update_countdown.cancel()
            
            update_countdown.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        global SENT_MESSAGE_IDS
        # Get the message object
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Get the member object
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        if member.bot:
            return

        sent_by_bot = False
        for i in self.SENT_MESSAGE_IDS:
            # Compare message ids
            if i==message.id:
                sent_by_bot = True
                break
        if not sent_by_bot:
            # IF not sent by bot, ignore
            return
            
        # Check if reaction made is allowed
        if str(payload.emoji) not in POLL_OPTION_EMOJIS:
            # Remove reaction
            await message.remove_reaction(payload.emoji, member)
            return

        # Remove duplicate votes of the user
        user_reaction_count = 0
        for r in message.reactions:
            async for u in r.users():
                if u.id == payload.user_id:
                    user_reaction_count+=1
                    if user_reaction_count>1:
                        await message.remove_reaction(payload.emoji, member)
                        break

    def validate_params(self, question, options, countdown):
        if question == "":
            return "Không được để trống câu hỏi"
        if len(options) <= 1:
            return "Phải có ít nhất 2 lựa chọn"
        if len(options) > 5:
            return "Chỉ có nhiều nhất 5 lựa chọn"
        if not isinstance(countdown, int):
            return "Thời gian phải là số nguyên dương"

        return None
        
def setup(bot):
    bot.add_cog(Poll(bot))  