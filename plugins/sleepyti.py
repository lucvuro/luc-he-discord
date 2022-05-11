from ast import expr_context
import json,requests
from datetime import datetime,timedelta
from dateutil.parser import parse
from discord.ext import commands
from discord import Embed

class sleep(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error,commands.CheckFailure):
            return await ctx.send("Server của bạn hiện tại không nằm trong whitelist!\nVui lòng liên hệ với chủ bot để được thêm vào whitelist")
        await ctx.send('Có lỗi xảy ra: {}'.format(str(error)))
    async def send_sleepcycle(self,ctx):
        try:
            time_api_url= "https://worldtimeapi.org/api/timezone/Asia/Bangkok"
            time_info = json.loads(requests.get(time_api_url).text)
            time_now_info = parse(time_info['datetime'])
            time_to_wake=[None]*6
            for i in range(len(time_to_wake)):
                temp = time_now_info + timedelta(hours=0,minutes=90*(i+1)+14)
                time_to_wake[i] = temp.strftime("%H:%M")
            time_to_wake_toString = "Bây giờ là {0}. Nếu bạn đi ngủ ngay bây giờ, bạn nên cố gắng thức dậy vào một trong những thời điểm sau: {1} hoặc {2} hoặc {3} hoặc {4} hoặc {5} hoặc {6} ".\
                    format(time_now_info.strftime("%H:%M"),time_to_wake[0],time_to_wake[1],time_to_wake[2],time_to_wake[3],time_to_wake[4],time_to_wake[5])
            return time_now_info.strftime("%H:%M"),time_to_wake
        except Exception as e:
            await ctx.reply(f"Có lỗi xảy ra: {e.__class__}")
    async def calculate_time_to_wake(self,ctx,time):
        format = "%H:%M"
        list_time = [None]*6
        try:
            time_after = datetime.strptime(time,format)
            for i in range(len(list_time)):
                temp = time_after - timedelta(hours=0,minutes=90*(i+1))
                list_time[i] = temp.strftime("%H:%M")
            return list_time[2:]
        except ValueError:
            await ctx.reply("Định dạng thời gian bạn nhập vào không đúng, (hh:mm)")
    @commands.command(name="sleepyti")
    async def sleepyti(self,ctx,*args):
        try:
            if len(args) >= 1:
                list_time = await self.calculate_time_to_wake(ctx,args[0])
                #Embed Start
                embed = Embed(colour=0x3498db,title="Chu kỳ giấc ngủ")
                embed.add_field(name=f":point_right: Để thức dậy vào lúc `{args[0]}`, bạn nên ngủ vào các khung giờ: ",value="\u200B",inline=False)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[3]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[2]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[1]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[0]}",inline=True)
                #Embed End
                await ctx.reply(embed=embed)
            else:
                time_now, list_time = await self.send_sleepcycle(ctx)
                #Embed Start
                embed = Embed(colour=0x3498db,title="Chu kỳ giấc ngủ")
                embed.add_field(name=f":point_right: Bây giờ là `{time_now}` :point_left:",value="\u200B",inline=False)
                embed.add_field(name=":bell: Nếu bây giờ bạn lên giường đi ngủ, bạn nên đặt báo thức vào các khung giờ sau:",value="\u200B",inline=False)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[0]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[1]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[2]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[3]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[4]}",inline=True)
                embed.add_field(name="\u200B",value=f":clock4: {list_time[5]}",inline=True)
                #Embed End
                await ctx.reply(embed=embed)
        except TypeError:
            pass
if __name__ == '__main__':
    sleep.calculate_time_to_wake('cac','cac','15:00')