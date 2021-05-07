from discord.ext import commands
from Lib import is_developer, agree_emoji, disagree_emoji


class CogEditor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["loadcog", "le", "lc"])
    @commands.check(is_developer)
    async def loadextension(self, ctx, Cog):
        try:
            self.bot.load_extension(f"Cogs.{Cog}")
            await ctx.message.add_reaction(agree_emoji())
        except Exception as error:
            await ctx.message.add_reaction(disagree_emoji())
            await ctx.send(f"Ошибка\n{error}")

    @commands.command(aliases=["reloadcog", "rle", "rlc"])
    @commands.check(is_developer)
    async def reloadextension(self, ctx, Cog):
        try:
            self.bot.reload_extension(f"Cogs.{Cog}")
            await ctx.message.add_reaction(agree_emoji())
        except Exception as error:
            await ctx.message.add_reaction(disagree_emoji())
            await ctx.send(f"Ошибка\n{error}")

    @commands.command(aliases=["unloadcog", "unle", "unlc", "ule", "ulc"])
    @commands.check(is_developer)
    async def unloadextension(self, ctx, Cog):
        try:
            self.bot.unload_extension(f"Cogs.{Cog}")
            await ctx.message.add_reaction(agree_emoji())
        except Exception as error:
            await ctx.message.add_reaction(disagree_emoji())
            await ctx.send(f"Ошибка\n{error}")


def setup(bot):
    bot.add_cog(CogEditor(bot))
