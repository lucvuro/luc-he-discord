import discord
from bandosao import BanDoSao
from discord import Embed,Attachment,Colour
from discord.ext.forms import Form
from discord.ext import commands
import json, datetime
class DatabaseBANDOSAO(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    # @commands.Cog.listener()
    # async def on_message(self,ctx):
    #     await self.check_add_user(ctx.author.id)
    async def check(self,userid):
        query = "SELECT * FROM users WHERE userid = $1"
        user = await self.bot.db.fetchrow(query,userid)
        if user is None:
            return False
        else:
            return True
    async def add_user(self,userid):
        check = await self.check(userid)
        if check == False:
            query = "INSERT INTO users (userid) VALUES ($1)"
            await self.bot.db.execute(query,userid)
            return True
        else:
            return False
    async def check_add_user(self,userid):
        if await self.check(userid) == True:
            pass
        else:
            await self.add_user(userid)
    async def check_bandosao(self,ctx):
        query = "SELECT * FROM users WHERE userid = $1"
        row_user = await self.bot.db.fetchrow(query,ctx.author.id)
        bandosao = row_user[1]
        if bandosao is None:
            return False
        else:
            return True
    async def add_bandosao(self,ctx,bandosao):
        try:
            query = "UPDATE users SET bandosao=$1 WHERE userid=$2"
            await self.bot.db.execute(query,bandosao,ctx.author.id)
            await ctx.reply("Tạo bản đồ sao thành công")
        except:
            await ctx.reply("Có lỗi trong quá trình tạo bản đồ sao")
    async def get_bandosao(self,ctx):
        query = "SELECT * FROM users WHERE userid = $1"
        user = await self.bot.db.fetchrow(query,ctx.author.id)
        bandosao = json.loads(user[1])
        return bandosao
    async def del_bandosao(self,ctx,userid):
        try:
            query = "UPDATE users SET bandosao=NULL WHERE userid=$1"
            await self.bot.db.execute(query,int(userid))
            return True
        except Exception as e:
            return e
    #Validate

    # @commands.command(name="add")
    # async def add(self,ctx):
    #     var = await self.add_user(ctx.author.id)
    #     if var == True:
    #         await ctx.reply("Thêm thành công")
    #     else:
    #         await ctx.reply("Không thành công vì đã tồn tại")
    @commands.command(name="test")
    async def test(self,ctx):
        await self.check_bandosao(ctx.author.id)
    # @commands.command(name='ketnoi')
    # async def ketnoi(self,ctx):
    #     check = await self.add_user(ctx.author.id)
    #     if check == True:
    #         await ctx.reply("Tạo tài khoản trên database thành công")
    #     else:
    #         await ctx.reply("Tài khoản đã có sẵn trên database")
    @commands.command(name='taobandosao')
    async def create_bandosao(self,ctx):
        await self.check_add_user(ctx.author.id)
        if await self.check_bandosao(ctx) == False:
            form = Form(ctx,"BẢN ĐỒ SAO CÁ NHÂN")
            form.add_question("Nhập đầy đủ HỌ VÀ TÊN của bạn",'hovaten')
            form.add_question("Giới tính của bạn là gì? (Nam/Nữ)",'gioitinh')
            form.add_question("Ngày tháng năm sinh của bạn là gì? (dd/mm/yyyy)",'ngaysinh')
            form.add_question("Giờ sinh của bạn là gì? (hh:mm)",'giosinh')
            form.edit_and_delete(True)
            result = await form.start()
            bandosao = BanDoSao(result.hovaten,result.gioitinh,result.ngaysinh,result.giosinh)
            if bandosao.check_type() == True:
                link_image,cungmattroi,cungmattrang,cungmoc = bandosao.taobandosao()
                #Embed
                # embed = Embed(colour=0x71368a,title="",description=f"Họ và tên: {result.hovaten}\nNgày sinh: {result.ngaysinh}\nGiới tính: {result.gioitinh}:male_sign:\nCung hoàng đạo: :leo:")
                # embed.set_image(url=f"{link_image}")
                # embed.set_author(name=f"Bản đồ sao của {ctx.author.name}")
                # embed.set_thumbnail(url=ctx.author.avatar_url)
                # embed.add_field(name="Cung Mọc",value=f"{cungmoc} :{BanDoSao.ten_tieng_anh_chd(cungmoc)}:")
                # embed.add_field(name="Cung Mặt Trời :sunny:",value=f"{cungmattroi} :{BanDoSao.ten_tieng_anh_chd(cungmattroi)}:",inline=False)
                # embed.add_field(name="Cung Mặt Trăng:crescent_moon:",value=f"{cungmattrang} :{BanDoSao.ten_tieng_anh_chd(cungmattrang)}:",inline=False)
                # await ctx.send(embed=embed)
                data_dict = {
                    'name': f'{result.hovaten}',
                    'gioitinh': f'{result.gioitinh}',
                    'ngaysinh': f'{result.ngaysinh}',
                    'giosinh': f'{result.giosinh}',
                    'link_image': f'{link_image}',
                    'cunghoangdao': f'{BanDoSao.ten_tieng_anh_chd(cungmattroi)}',
                    'cungmoc': f'{BanDoSao.ten_tieng_anh_chd(cungmoc)}',
                    'cungmattroi': f'{BanDoSao.ten_tieng_anh_chd(cungmattroi)}',
                    'cungmattrang': f'{BanDoSao.ten_tieng_anh_chd(cungmattrang)}'
                }
                data_json = json.dumps(data_dict)
                await self.add_bandosao(ctx,data_json)
            else:
                await ctx.reply("Có lỗi xảy ra: Thông tin bạn nhập không đúng")
        else:
            await ctx.reply("Ủa! Có rồi tạo chi nữa bạn")
    @commands.command(name='bandosao')
    async def bandosao(self,ctx):
        await self.check_add_user(ctx.author.id)
        if await self.check_bandosao(ctx) == True:
            bandosao = await self.get_bandosao(ctx)
            cungmoc = BanDoSao.get_chd(bandosao['cungmoc'],'name')
            cungmattroi = BanDoSao.get_chd(bandosao['cungmattroi'],'name')
            cungmattrang = BanDoSao.get_chd(bandosao['cungmattrang'],'name')
            sign_sex = ':male_sign:' if bandosao['gioitinh'].lower() == 'nam' else ':female_sign:'
            # Embed Start
            embed = Embed(colour=0x71368a,title="",description=f"Họ và tên: {bandosao['name']}\nNgày sinh: {bandosao['ngaysinh']}\nGiới tính: {bandosao['gioitinh']} {sign_sex}\nCung hoàng đạo: :{bandosao['cunghoangdao']}:")
            embed.set_image(url=f"{bandosao['link_image']}")
            embed.set_author(name=f"Bản đồ sao của {ctx.author.name}")
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="Cung Mọc",value=f"{cungmoc} :{bandosao['cungmoc']}:")
            embed.add_field(name="Cung Mặt Trời :sunny:",value=f"{cungmattroi} :{bandosao['cungmattroi']}:",inline=False)
            embed.add_field(name="Cung Mặt Trăng:crescent_moon:",value=f"{cungmattrang} :{bandosao['cungmattrang']}:",inline=False)
            await ctx.send(embed=embed)
            # Embed End
        else:
            await ctx.reply("Bạn chưa có bản đồ sao, vui lòng !taobandosao")
    @commands.command(name="delete")
    async def delete(self,ctx,*args):
        await self.check_add_user(ctx.author.id)
        if ctx.author.id == 163990753557741568:
            if args[0] == 'bandosao':
                xoa = await self.del_bandosao(ctx,args[1])
                if xoa == True:
                    await ctx.reply("Xóa bản đồ sao thành công cho")
                else:
                    await ctx.reply(f"Có lỗi xảy ra khi xóa: {xoa}")
        else:
            await ctx.reply("Có lỗi xảy ra")
