import os
import json
from discord import Embed,Attachment,Colour
from discord.ext import commands
from discord.ext.forms import Form
from dotenv import load_dotenv
import asyncpg
import database
from plugins.bandosao import BanDoSao
from plugins import sleepyti,music1
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
my_whitelist = [883625186333704252,646989878055403521,881153070111809628]
bot = commands.Bot(command_prefix="~", help_command=None)
@bot.check_once
async def whitelist(ctx):
    return ctx.guild.id in my_whitelist
bot.add_cog(database.DatabaseBANDOSAO(bot))
bot.add_cog(sleepyti.sleep(bot))
bot.add_cog(music1.Music(bot))
#Connect to database
async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn='postgres://lktbgprxgsumxy:a50f0706ca87bdaa5af8dced7615edc569a291de7d5fb221db417d3d6aadd4ec@ec2-52-3-200-138.compute-1.amazonaws.com:5432/d2jn5aebkji9uh')
    # bot.db = await asyncpg.create_pool(dsn='postgres://postgres:lucvu123@localhost:5432/discord')
    print("Ket noi toi database thanh cong")

@bot.event
async def on_ready():
    print(f'{bot.user.name} da ket noi toi may chu thanh cong')
# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.MissingRequiredArgument):
#         await ctx.reply(f'Lệnh của bạn chưa đúng cú pháp',mention_author=True)

#Database Interact
# @bot.command(name="createtable")
# async def createtable(ctx,guildid):
#     if ctx.author.id == 163990753557741568:
#         await bot.db.execute(f'CREATE TABLE IF NOT EXISTS {guildid} (userid BIGINT NOT NULL PRIMARY KEY, bandosao JSON)')
#     else:
#         await ctx.reply("Bạn không thể thực hiện lệnh này")

# @bot.command(name="hello")
# async def hello(ctx,userid):
#     row = await bot.db.fetchrow(f'SELECT * FROM users WHERE userid = {userid}')
#     print(row is None)


# @bandosao.error
# async def ngaysinh_error(ctx,error):
#     if isinstance(error, commands.errors.MissingRequiredArgument):
#         await ctx.reply(f'Lệnh của bạn chưa đúng cú pháp',mention_author=True)

@bot.command(name="help")
async def help(ctx,*args):
    if len(args) >= 1:
        if args[0] == 'bandosao':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh bandosao",description=f"Xem bản đồ sao của bản thân")
            embed.add_field(name="Sử dụng",value=f"`~bandosao`")
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'taobandosao':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh taobandosao",description=f"Tạo bản đồ sao cho cá nhân và lưu nó vào database")
            embed.add_field(name="Sử dụng",value=f"`~taobandosao`")
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'sleepyti':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh sleepyti",description=f"Chu kỳ giấc ngủ")
            embed.add_field(name="Sử dụng",value=f"`~sleepyti`\n`~sleepyti` + time(hh:mm)")
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'play': #Mo dau lenh bot music
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh play",description=f"Tìm nhạc rồi phát hoặc phát trực tiếp từ link")
            embed.add_field(name="Sử dụng",value=f"`~play` + tenbaihat\n`~play` + url")
            embed.add_field(name="Viết tắt",value=f"`~p`",inline=False)
            embed.add_field(name="Các đối số truyền vào",value=f"* `~tenbaihat` có thể là nguyên cái tên bài hát hoặc từ khóa cũng được\n* `url` là link video, hiện tại chỉ xài được link **Youtube** mà thâu",inline=False)
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'queue':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh queue",description=f"Xem danh sách các bài nhạc")
            embed.add_field(name="Sử dụng",value=f"`~queue`")
            embed.add_field(name="Viết tắt",value=f"`~q`",inline=False)
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'skip':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh skip",description=f"Nhảy nhạc như nhảy việc")
            embed.add_field(name="Sử dụng",value=f"`~skip`")
            embed.add_field(name="Viết tắt",value=f"`~s`",inline=False)
            await ctx.send(embed=embed)
            # Embed End  
        elif args[0] == 'stop':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh stop",description=f"Dừng nhạc rồi out khỏi voice, dứt khoát không động tác thừa")
            embed.add_field(name="Sử dụng",value=f"`~stop`")
            await ctx.send(embed=embed)
            # Embed End  
        elif args[0] == 'loop':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh loop",description=f"Loop bài nhạc hiện tại đang phát cho đến khi bạn tắt")
            embed.add_field(name="Sử dụng",value=f"`~loop`")
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'shuffle':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh shuffle",description=f"Trộn danh sách nhạc như trộn bịch bánh trán")
            embed.add_field(name="Sử dụng",value=f"`~shuffle`")
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'nowplaying':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh nowplaying",description=f"Như cái tên lệnh, cho biết mình đang playing gì vào lúc nowy`")
            embed.add_field(name="Sử dụng",value=f"`~nowplaying`")
            embed.add_field(name="Viết tắt",value=f"`~np`",inline=False)
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'remove':
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh remove",description=f"Xóa 1 bài chỉ định ra khỏi danh sách nhạc")
            embed.add_field(name="Sử dụng",value=f"`~remove` + number")
            embed.add_field(name="Các đối số truyền vào",value=f"* `~number` như tên đối số, là **1 con số** thứ tự của bài hát bạn muốn xóa",inline=False)
            await ctx.send(embed=embed)
            # Embed End
        elif args[0] == 'join': #Ket thuc lenh bot music
            # Embed Start
            embed = Embed(colour=0x3498db,title="Lệnh join",description=f"Tên như lệnh, mà lệnh như tên, join vô kênh voice bạn đang trong đó")
            embed.add_field(name="Sử dụng",value=f"`~join`")
            await ctx.send(embed=embed)
            # Embed End      
    else:
        # Embed Start
        embed = Embed(colour=0x3498db,title="Danh sách lệnh")
        embed.add_field(name=":six_pointed_star: Chiêm Tinh",value=f"`taobandosao`, `bandosao`")
        embed.add_field(name=":bulb: Tiện Ích",value=f"`sleepyti`",inline=False)
        embed.add_field(name=":musical_note: Âm Nhạc",value=f"`play`, `queue`, `skip`, `stop`, `loop`, `shuffle`, `nowplaying`, `remove`, `join`",inline=False)
        await ctx.send(embed=embed)
        # Embed End
bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)