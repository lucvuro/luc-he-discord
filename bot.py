import os
import json
from discord import Embed,Attachment,Colour
from discord.ext import commands
from discord.ext.forms import Form
from dotenv import load_dotenv
import asyncpg
import database
from bandosao import BanDoSao
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")
bot.add_cog(database.DatabaseBANDOSAO(bot))
#Connect to database
async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn='postgres://postgres:lucvu123@localhost:5432/discord')
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

bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)