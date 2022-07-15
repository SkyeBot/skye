from typing import Dict, Union
import discord
from discord.ext import commands

from core.bot import SkyeBot

from .tags import Tags

class tags(Tags):
    """All tag commands"""

async def setup(bot: SkyeBot):
    await bot.add_cog(tags(bot))