import discord
import time
import json
from discord.ext import commands
from Lib import get_guild_language, disagree_emoji, lang, config


class MainCog(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.uptime = time.time()
        with open("Database/Statistic.json", "rb") as read_f:
            self.statistic = json.load(read_f)

    '''@commands.command(aliases=["Help", "h"])
    async def help(self, ctx, arg1=None):
        language = await get_guild_language(ctx)
        settings = ['settings', 'Settings', 's']
        if arg1 is None:
            await help_list(ctx)
        elif arg1 in settings:
            await help_settings(ctx)
        else:
            await ctx.send(f"{lang[language]['Parameter']} `{arg1}` {lang[language]['NotFound']}")'''

    @commands.command()
    async def ping(self, ctx):
        glang = await get_guild_language(ctx)
        uptime = time.gmtime(time.time() - self.uptime)
        ping = round(self.bot.latency * 1000, 2)
        if ping < 160:
            color = discord.Colour.green()
        elif ping < 200:
            color = discord.Colour.orange()
        else:
            color = discord.Colour.red()
        embed = discord.Embed(title=f"{lang[glang]['Pong']}!",
                              description=f"{lang[glang]['Ping']}: `{ping}ms`\nUptime {uptime.tm_hour + ((uptime.tm_mday - 1) * 24)}h {uptime.tm_min}m {uptime.tm_sec}s",
                              color=color)
        await ctx.send(embed=embed)

    @commands.command(aliases=["Invite", "i"])
    async def invite(self, ctx):
        embed = discord.Embed(title=lang[await get_guild_language(ctx)]['Invite'], url=config["invite"],
                              color=0x7289da)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["d", 'Donate'])
    async def donate(self, ctx):
        language = await get_guild_language(ctx)
        if language == "ru":
            embed = discord.Embed(title="Донат",
                                  description="Если вам вдруг захочется поддержать автора проекта, то вы смело можете это сделать:\n[QIWI](https://qiwi.com/n/THEKINGOFTIME)\nНа карту: 4276400029387983",
                                  colour=discord.Colour.from_rgb(217, 171, 42))
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        else:
            embed = discord.Embed(title="Donate",
                                  description="Donation unavailable in your country",
                                  colour=discord.Colour.from_rgb(217, 171, 42))
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(str(None))

    @commands.Cog.listener()
    async def on_ready(self):
        print('TimeGuard_v2 инициализирован')
        if self.statistic["head"]["active_mode"]:
            text = 'Фильрую опасный контент'
        else:
            text = "Анализирую данные"
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=text))

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #    current_content = message.content.lower()
    #    current_content = current_content.replace(" ", "")
    #    if (("пидор" in current_content) or ("пидар" in current_content)) and developer() in message.mentions and is_pidor():
    #        try:
    #            await message.add_reaction("🇳")
    #            await message.add_reaction("🇴")
    #            await message.add_reaction("⬛")
    #            await message.add_reaction("🇺")
    #        except:
    #            await message.reply(":regional_indicator_n::regional_indicator_o:⬛🇺")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            language = "ru"
        except TypeError:
            language = 'ru'
        if isinstance(error, commands.CommandNotFound):
            pass
            # await ctx.send(str(lang()[language]["UnKnCommand"]))
            # await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.BadArgument):
            await ctx.send(str(lang[language]["BArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(lang[language]["MissReqArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(lang[language]["AccessDenied"]))
            await ctx.message.add_reaction(disagree_emoji())
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(str(lang[language]["Bot_hvnt_perm"]))
            await ctx.message.add_reaction(disagree_emoji())


def setup(bot):
    bot.add_cog(MainCog(bot))
