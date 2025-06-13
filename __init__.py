from redbot.core.bot import Red
from .updatemasking import UpdateMasking


async def setup(bot: Red):
    cog = UpdateMasking(bot)
    await bot.add_cog(cog)
