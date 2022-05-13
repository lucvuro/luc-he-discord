from discord import Embed,Attachment,Colour,Game,User
from discord.ext import commands
from discord_components import DiscordComponents, ComponentsBot, Button
from plugins.databasejson import DatabaseJson
class NotSetupError(Exception):
    pass
class AdminMenu(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.data = None
    async def add_to_database(self,ctx):
        self.data = DatabaseJson(ctx.guild.id)
    async def cog_check(self, ctx):
        if DatabaseJson.check_setup(ctx.guild.id) == False:
            raise NotSetupError
        return True
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error,commands.CheckFailure):
            return await ctx.send("Server của bạn hiện tại không nằm trong whitelist!\nVui lòng liên hệ với chủ bot để được thêm vào whitelist")
        if isinstance(error,NotSetupError):
            return await ctx.send("Bạn chưa setup bot cho chức năng này, vui lòng ~setup")
        await ctx.send('Có lỗi xảy ra: {}'.format(str(error)))
    async def cog_before_invoke(self, ctx: commands.Context):
        await self.add_to_database(ctx)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def _kick(self,ctx: commands.Context,user:User,reason=None):
        if reason is None:
            ctx.send("alo")
    @commands.command(name="menu")
    @commands.has_permissions(administrator=True)
    async def _menu(self,ctx:commands.Context, user: User):
        await ctx.send(
        f"Bạn muốn làm gì {user.mention}",
        components = [
            [
                Button(label = "Kick", custom_id = "kick",style=4),
                Button(label = "Ban", custom_id = "ban",style=4),
                Button(label = "Mute", custom_id = "mute",style=4),
                Button(label = "Timeout", custom_id = "timeout",style=4),
                Button(label = "Bot Ban", custom_id = "botban",style=4)
            ],
            [
                Button(label = "Unmute", custom_id = "unmute",style=3),
                Button(label = "Thêm Role", custom_id = "addrole",style=3),
                Button(label = "Unban Bot", custom_id = "unbanbot",style=3)
            ],
            [
                Button(label = "Đổi Nickname", custom_id = "nickname",style=2),
                Button(label = "Xóa Role", custom_id = "rmrole",style=2)
            ]
        ],
    )
    