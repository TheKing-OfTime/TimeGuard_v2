import asyncio
import discord
import json
from discord.ext import commands
from Lib import is_developer, disagree_emoji, loading_emoji, agree_emoji


class AntiCrashAttachments(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        with open("Database/Statistic.json", "rb") as read_f:
            self.statistic = json.load(read_f)

        with open("Database/cache.json", "rb") as read_f:
            self.cache = json.load(read_f)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open("Database/Statistic.json", "w") as write_f:
            json.dump(self.statistic, write_f)

        with open("Database/cache.json", "w") as write_f:
            json.dump(self.cache, write_f)

    @commands.Cog.listener()
    @commands.bot_has_permissions(manage_messages=True)
    async def on_message(self, message: discord.Message):
        lst = message.attachments
        crash_detected = False
        if message.content in self.cache["black_listed_links"]:
            crash_detected = True
            self.statistic["head"]["auto_crash_content"] += 1
            self.statistic["data"].append({"type": "black_listed_links",
                                           "message_id": message.id,
                                           "detected_content": message.content,
                                           "is_crush_auto": True,
                                           "is_crush": None
                                           })
        if len(lst) != 0 and crash_detected == False:
            try:
                reaction = True
                await message.add_reaction(loading_emoji())
            except:
                reaction = None
        else:
            reaction = None

        for attachment in lst:
            if attachment.url in self.cache["black_listed_links"]:
                crash_detected = True
                self.statistic["head"]["auto_crash_content"] += 1
                self.statistic["data"].append({"type": "black_listed_links",
                                               "message_id": message.id,
                                               "detected_content": message.content,
                                               "attachment_id": attachment.id,
                                               "attachment_url": attachment.url,
                                               "is_crush_auto": True,
                                               "is_crush": None
                                               })
                break
            else:
                self.statistic["head"]["counter"] = len(self.statistic["data"])
                attachment_bytes = await attachment.read()

                dead_bytes = str(attachment_bytes).count("00")
                all_bytes = len(str(attachment_bytes))
                probability_of_crash_content = round(dead_bytes / all_bytes * 1000, 2)

                # print(dead_bytes, all_bytes, f"\nВероятность краш контента {probability_of_crash_content}%")

                if probability_of_crash_content > self.statistic["head"]["detect_ratio"]:
                    self.statistic["head"]["auto_crash_content"] += 1
                self.statistic["data"].append({"type": "probability",
                                               "message_id": message.id,
                                               "attachment_id": attachment.id,
                                               "attachment_url": attachment.url,
                                               "dead_bytes": dead_bytes,
                                               "all_bytes": all_bytes,
                                               "probability": probability_of_crash_content,
                                               "is_crush_auto": True if probability_of_crash_content >
                                                                        self.statistic["head"][
                                                                            "detect_ratio"] else False,
                                               "is_crush": None
                                               })
                if probability_of_crash_content > self.statistic["head"]["detect_ratio"]:
                    self.cache["black_listed_links"].append(attachment.url)
        self.statistic["head"]["counter"] = len(self.statistic["data"])

        with open("Database/Statistic.json", "w") as write_f:
            json.dump(self.statistic, write_f)
        with open("Database/cache.json", "w") as write_f:
            json.dump(self.cache, write_f)

        if reaction is not None:
            await message.remove_reaction(loading_emoji(), message.guild.me)
        if crash_detected:
            probability_of_crash_content = self.statistic["head"]["detect_ratio"] + 1
        if probability_of_crash_content < self.statistic["head"]["detect_ratio"]:
            if reaction is not None:
                await message.add_reaction(agree_emoji())
                await asyncio.sleep(3)
                await message.remove_reaction(agree_emoji(), message.guild.me)
        else:
            if self.statistic["head"]["active_mode"]:
                await message.delete()
                await message.channel.send(f"Заблокирован опасный контент от пользователя: {message.author.mention}", delete_after=5)
            else:
                await message.add_reaction(disagree_emoji())

    @commands.command()
    async def get_stat(self, ctx: commands.Context, _type="default", numb=0):
        _type_aliases_v1 = ["detail", "d", "more", "m"]
        embed = discord.Embed(colour=discord.Colour.blurple())
        if _type == "default":
            embed.title = "Сводка"
            embed.add_field(name="Проанализированных файлов:", value=self.statistic["head"]["counter"], inline=False)
            embed.add_field(name="Подозрительных из них:", value=self.statistic["head"]["auto_crash_content"],
                            inline=False)
            embed.add_field(name="Активный режим:", value=self.statistic["head"]["active_mode"], inline=False)
            embed.add_field(name="Порог детекта:", value=self.statistic["head"]["detect_ratio"], inline=False)
        elif _type in _type_aliases_v1:
            embed.title = "Инфо по случаю"
            if not int(numb) + 1 > len(self.statistic["data"]):
                for item in self.statistic["data"][numb].items():
                    embed.add_field(name=item[0], value=item[1], inline=False)
            else:
                raise commands.BadArgument
        await ctx.send(embed=embed)

    @commands.command(aliases=["s"])
    @commands.check(is_developer)
    async def settings(self, ctx: commands.Context, option: str, value: str):
        try:
            if option in ["active_mode", "active", 'a']:
                if value == 'on':
                    self.statistic["head"]["active_mode"] = True
                    await self.bot.change_presence(
                        activity=discord.Activity(type=discord.ActivityType.playing, name='Фильрую опасный контент'))
                    await ctx.message.add_reaction(agree_emoji())
                elif value == 'off':
                    self.statistic["head"]["active_mode"] = False
                    await self.bot.change_presence(
                        activity=discord.Activity(type=discord.ActivityType.playing, name="Анализирую данные"))
                    await ctx.message.add_reaction(agree_emoji())
                else:
                    raise commands.BadArgument

            elif option in ["detect_ratio", "ratio", 'r']:
                self.statistic["head"]["detect_ratio"] = int(value)
                await ctx.message.add_reaction(agree_emoji())
        except Exception as error:
            await ctx.send(f"Ошибка: {error}")


def setup(bot):
    bot.add_cog(AntiCrashAttachments(bot))
