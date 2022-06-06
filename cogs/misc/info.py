from code import interact
from collections import Counter
import discord

from discord.ext import commands

from discord import app_commands
from discord.app_commands import Choice

from typing import Union, Optional

#Local imports
from core.bot import SkyeBot
from utils import default, time, format
from utils.context import Context

class Dropdown(discord.ui.Select):
    def __init__(self, ctx: Union[Context, discord.Interaction], bot: SkyeBot,member: discord.Member):
        self.ctx = ctx
        self.member = member
        self.bot = bot

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='avatar', description='Avatar of the user', emoji='🟥'),
            discord.SelectOption(label='banner', description='The Banner of the user', emoji='🟩'),
            discord.SelectOption(label='info', description='Actual userinfo', emoji='🟦'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.

        if isinstance(self.ctx, discord.Interaction):
            user = self.ctx.user.id
        else:
            user = self.ctx.author.id

        if interaction.user.id != user:
            pass
        else:
            await interaction.response.defer()

        if self.member is None:
            self.member = self.ctx.user        


        if self.values[0] == "banner":
            user = await interaction.client.fetch_user(self.member.id)

            embed = discord.Embed(description=f"{user.mention} Banner",color=0x3867a8)
    
            if user.banner is None:
                embed.description = "User does not have a banner!"
            else:
                embed.set_image(url=user.banner.url)
        
            
            await interaction.message.edit(embed=embed, view=DropdownView(interaction,self.member))

        if self.values[0] == "avatar":
            embed = discord.Embed(description=f"{self.member.mention} avatar", color=0x3867a8)
            embed.set_image(url=self.member.display_avatar.url)
            await interaction.message.edit(embed=embed, view=DropdownView(interaction,self.member))

        if self.values[0] == "info":
            member = self.member

            member = interaction.guild.get_member(self.member.id)

            created_date = default.date(self.member.created_at, ago=True)
            joined_date = default.date(self.member.joined_at, ago=True)

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(self.member.roles, key=lambda x: x.position, reverse=True) if x.id != interaction.guild.default_role.id]
            ) if len(member.roles) > 1 else "None"

            embed = discord.Embed(description=f"**Info About {member.mention}**", color=0x3867a8)

            embed.add_field(name="ID", value=self.member.id)
            embed.add_field(name="Created At", value=created_date,inline=True)
            embed.add_field(name="Joined At", value=joined_date)
            embed.add_field(name="Roles", value=f"**{show_roles}**",inline=True)
            embed.add_field(name="Status", value=f"{str(self.member.status)}")
            embed.set_author(name=self.member, icon_url=self.member.display_avatar.url)
            embed.set_thumbnail(url=self.member.display_avatar.url)
    

            await interaction.message.edit(embed=embed)


            

            


class DropdownView(discord.ui.View):
    def __init__(self, ctx: Union[Context, discord.Interaction],bot: SkyeBot, member=None):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        # Adds the dropdown to our view object.
        self.add_item(Dropdown(self.ctx,self.bot,member))



    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if isinstance(self.ctx, discord.Interaction):
            user = self.ctx.user.id
        else:
            user = self.ctx.author.id


        if interaction.user.id == user:
            return True
        else:
            await interaction.response.send_message(f"You cant use this as you're not the command invoker, only the author (<@{user}>) Can Do This!", ephemeral=True)
            return False

class Misc(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @app_commands.command(name="userinfo")
    @app_commands.guild_only()
    async def userinfo_slash(self, itr: discord.Interaction, member: Optional[discord.Member]=None):
        member = member or itr.user
        
        member = itr.guild.get_member(member.id)

        view = DropdownView(itr,self.bot,member)

        created_date = default.date(member.created_at, ago=True)
        joined_date = default.date(member.joined_at, ago=True)

        show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if x.id != itr.guild.default_role.id]
        ) if len(member.roles) > 1 else "None"

        embed = discord.Embed(description=f"**Info About {member.mention}**", color=self.bot.color)

        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Created At", value=created_date,inline=True)
        embed.add_field(name="Joined At", value=joined_date)
        embed.add_field(name="Roles", value=f"**{show_roles}**",inline=True)
        embed.add_field(name="Status", value=f"{str(member.status)}")
        self.bot.logger.info(member.status)
        self.bot.logger.info(self.bot.intents)
        embed.set_author(name=member, icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await itr.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="serverinfo")
    async def serverinfo(self, interaction: discord.Interaction, *, guild_id: str  = None):
        """Shows info about the current server."""
        
        if guild_id is not None and await self.bot.is_owner(interaction.user):
            guild = self.bot.get_guild(int(guild_id))
            if guild is None:
                return await interaction.response.send_message(f'Invalid Guild ID given.')
        else:
            guild = interaction.guild

        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        if not guild.chunked:
            await guild.chunk(cache=True)

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed()
        e.title = guild.name
        e.description = f'**ID**: {guild.id}\n**Owner**: {guild.owner}'
        if guild.icon:
            e.set_thumbnail(url=guild.icon.url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: '<:text_channel:586339098172850187>',
            discord.VoiceChannel: '<:voice_channel:586339098524909604>',
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} ({secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        info = []
        features = set(guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner',
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'{self.bot.tick(True)}: {label}')

        if info:
            e.add_field(name='Features', value='\n'.join(info))

        e.add_field(name='Channels', value='\n'.join(channel_info))

        if guild.premium_tier != 0:
            boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts}\nLast Boost: {last_boost} ({time.format_relative(last_boost.premium_since)})'
            e.add_field(name='Boosts', value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f'Total: {guild.member_count} ({format.plural(bots):bot})'

        e.add_field(name='Members', value=fmt, inline=False)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available

        fmt = (
            f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n'
            f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n'
        )
        if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f'{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit*2}'
        e.add_field(name='Emoji', value=fmt, inline=False)
        e.set_footer(text='Created').timestamp = guild.created_at
        await interaction.response.send_message(embed=e)