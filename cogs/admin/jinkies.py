from __future__ import annotations

from io import BytesIO
import string
import aiohttp
import discord
from discord.ext import commands

from datetime import datetime

from typing import Union, List

from utils.context import Context

from core.bot import SkyeBot

from PIL import Image, ImageDraw, ImageFont, ImageChops
from discord import app_commands

class TestView(discord.ui.View):
    def __init__(self, ctx: Union[Context, discord.Interaction], member: discord.Member):
        self.member = member
        self.ctx = ctx

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.defer()
        return False

    async def start(self):
        self.message = await self.ctx.send(view=self)

class MyModal(discord.ui.Modal, title='Cock'):
    def __init__(self, channels: discord.TextChannel):
        super().__init__()
        self.channels: discord.TextChannel = channels
        self.foo = discord.ui.Select(options=[discord.SelectOption(label=f"#{x.name}") for x in channels])
        self.add_item(self.foo)




    async def on_submit(self, interaction):
        a = ''.join(x.mention for x in interaction.guild.channels if f"#{x.name}" == self.foo.values[0])
        
        await interaction.response.send_message(f'The Channel You Picked: {a} ', ephemeral=True)
    

class Yoink(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    def circle(self,pfp,size = (215,215)):
    
        pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")

        bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(pfp.size, Image.ANTIALIAS)
        mask = ImageChops.darker(mask, pfp.split()[-1])
        pfp.putalpha(mask)
        return pfp

    @app_commands.command()
    async def hithere(self, itr:discord.Interaction):
        
        await itr.response.send_modal(MyModal([x for x in itr.guild.channels if type(x) is discord.TextChannel]))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        members: List[discord.Member] = await guild.chunk(cache=True) if not guild.chunked else guild.members

        

        for member in members:
            if member.mutual_guilds or member == member.guild.me:
                continue
            
            avatar = await member.display_avatar.read()

            await self.bot.pool.execute("""
            INSERT INTO avatars (user_id, time_changed, avatar)
            VALUES ($1, $2, $3)
            """, member.id, discord.utils.utcnow(), avatar)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.mutual_guilds:
            return
        
        avatar = await member.display_avatar.read()
        await self.bot.pool.execute("""
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """, member.id, discord.utils.utcnow(), avatar)

    @commands.Cog.listener()
    async def on_user_avatar_update(self, _: discord.User, after: discord.User):
        avatar = await after.display_avatar.read()

        await self.bot.pool.execute("""
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """, after.id, discord.utils.utcnow(), avatar)


    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)
    
    async def get_banner(self, banner_url):
        async with self.bot.session.get(banner_url) as resp:
            bytes = await resp.read()
            
        return bytes

    @commands.command()
    async def asss(self, ctx: Context):
        await ctx.send([(f"channel: {channel.name}") for channel in ctx.guild.channels])

    @commands.command()
    async def pil_test(self, ctx: Context, user: discord.Member=None):
        user = user.id or ctx.author.id
        user = await self.bot.fetch_user(user)
        
        output_buffer = BytesIO()

        image = Image.new('RGBA',(1000, 500))

        pfp = user.avatar.replace(size=256).with_static_format('jpg')
        data = BytesIO(await pfp.read())

        pfp = Image.open(data).convert("RGBA")
        


        image_x, image_y = image.size

        banner = Image.open('./ass.jpg')



        canvas_to_banner_ratio = image_y / banner.height
        banner = banner.resize((int(banner.width * canvas_to_banner_ratio), image_y ))

        image.paste(banner)

        I1 = ImageDraw.Draw(image)

        image.paste(pfp, (int(image_x / 20), int(image_y / 3)))



        font = ImageFont.truetype("./Nunito-Regular.ttf",38)

        # Usually, .paste pastes from the top left, so let's an offset of 1/4 the image width, and 1/2 the height
        I1.text((int(image_x / 2), int(image_y / 2)), text=f"fuck you: {user}", font=font)

        

        image.save(output_buffer, "png")  # or whatever format
        output_buffer.seek(0)

        await ctx.send(file=discord.File(fp=output_buffer, filename="my_file.png"))

    @commands.command()
    async def wel(self, ctx: Context):
        text_db = str(await self.bot.pool.fetchval("SELECT message FROM welcome_config WHERE guild_id = $1", ctx.guild.id))
        
        new_text = string.Template(text_db).safe_substitute(
            user=ctx.author.mention,
            guild=ctx.guild
        )

        await ctx.send(new_text)

    @commands.command()
    async def api_check(self, ctx: Context):
        message = await ctx.send("a")

        async with self.bot.session.get("https://sawsha-is.gay/vYyj0P8.png") as resp:
            image = BytesIO.read(resp.read())

        await message.edit(attachments=discord.File(image, filename="vYyj0P8.png"))

    async def idkfunctionnameig(self, api_url: str):
        async with self.bot.session.get(api_url) as response:
            json = await response.json()
        
        return json

    @commands.command()
    async def helper_func(self, ctx: Context):
        data = await self.idkfunctionnameig("https://users.roblox.com/v1/users/36178192")
        await ctx.send(data)
        await ctx.db

    @commands.command()
    async def invitetest(self, ctx: Context):
        a = '\n\n'.join(f"Invite: <{x.url}> \nInvite Creator: {x.inviter}" for x in await ctx.guild.invites())
        await ctx.send(a)
    

async def setup(bot):
    await bot.add_cog(Yoink(bot))