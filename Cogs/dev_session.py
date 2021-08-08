import time

import discord
import time
import onetimepass
import json
from discord.ext import commands
from Lib import is_developer, disagree_emoji, loading_emoji, agree_emoji, config, random_base32, Session_close, is_developer_2fa


class DevSessionCreator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        with open("Database/cache.json", "rb") as read_f:
            self.cache = json.load(read_f)

    @commands.command()
    @commands.check(is_developer)
    async def generate_secret(self, ctx: commands.Context):
        secret = random_base32()
        print(secret)
        await ctx.message.add_reaction(agree_emoji())

    @commands.command()
    @commands.check(is_developer)
    async def session_create(self, ctx: commands.Context, token: str):
        if int(onetimepass.get_totp(config["secret_v1"])) == int(token):
            print(self.cache["session"]["guild_id"])
            if self.cache["session"]["guild_id"] is None:
                self.cache["session"]["is_session"] = True
                self.cache["session"]["guild_id"] = ctx.guild.id
                self.cache["session"]["last_action_unix"] = time.time()
                with open("Database/cache.json", "w") as write_f:
                    json.dump(self.cache, write_f)
                await ctx.message.add_reaction(agree_emoji())
                await ctx.send("Защищённая сессия разработчика создана. Сессия может быть запущена только на одном сервере.\nСессия закроется автоматически после 5 минут бездействия")
            else:
                await ctx.message.add_reaction(disagree_emoji())
                await ctx.send("Сессия создана на другом сервере")
        else:
            await ctx.message.add_reaction(disagree_emoji())
            await ctx.send("Не верный код аутентификации")

    @commands.command()
    @commands.check(is_developer)
    async def session_close(self, ctx: commands.Context):
        if Session_close(ctx):
            await ctx.message.add_reaction(agree_emoji())
            await ctx.send("Сессия закрыта")
        else:
            await ctx.message.add_reaction(disagree_emoji())
            await ctx.send("Сессия создана на другом сервере")

    @commands.command()
    @commands.check(is_developer_2fa)
    async def test(self, ctx):
        await ctx.send("Успех")


def setup(bot):
    bot.add_cog(DevSessionCreator(bot))
