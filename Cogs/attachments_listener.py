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
    async def on_message(self, message: discord.Message):

        is_detected = False

        for link in self.cache["black_listed_links"]:
            if link in message.content:
                is_detected = True
                self.statistic["data"].append({
                    "type": "by_bl_link_in_message",
                    "message_id": message.id,
                    "is_crush_auto": True,
                    "is_crush": None
                })
                break

        if not is_detected and message.attachments != []:

            if self.statistic["head"]["visualisation_mode"] == 2:
                await message.add_reaction(loading_emoji())

            for attachment in message.attachments:
                if attachment.content_type.startswith('video') or attachment.content_type == "image/gif":
                    if attachment.url in self.cache["black_listed_links"]:
                        is_detected = True
                        self.statistic["data"].append({
                            "type": "by_bl_link_in_attachment",
                            "message_id": message.id,
                            "attachment_id": attachment.id,
                            "attachment_url": attachment.url,
                            "is_crush_auto": True,
                            "is_crush": None
                        })
                        break
                    else:
                        attachment_content = str(await attachment.read())
                        empty_bytes = attachment_content.count("00")
                        all_bytes = attachment.size
                        probability = round(empty_bytes/all_bytes*1000, 3)

                        #print(empty_bytes, all_bytes, probability)

                        if probability >= int(self.statistic["head"]["detect_ratio"]):
                            is_detected = True
                            self.statistic["data"].append({
                                "type": "by_empty_bytes",
                                "message_id": message.id,
                                "attachment_id": attachment.id,
                                "attachment_url": attachment.url,
                                "empty_bytes": empty_bytes,
                                "all_bytes": all_bytes,
                                "probability": probability,
                                "detect_ratio": self.statistic["head"]["detect_ratio"],
                                "is_crush_auto": True,
                                "is_crush": None
                            })

                            self.cache["black_listed_links"].append(attachment.url)

                            break

        if is_detected:
            self.statistic["head"]["counter"] = len(self.statistic["data"])
            self.statistic["head"]["auto_crash_content"] += 1

            if self.statistic["head"]["active_mode"]:
                await message.delete()
                await message.channel.send(f"Удалён опасный контент от {message.author.mention}", delete_after=5)
            else:
                if self.statistic["head"]["visualisation_mode"] == 2:
                    await message.remove_reaction(loading_emoji(), message.guild.me)
                    await message.add_reaction(disagree_emoji())
                elif self.statistic["head"]["visualisation_mode"] == 1:
                    await message.add_reaction(disagree_emoji())

            with open("Database/Statistic.json", "w") as write_f:
                json.dump(self.statistic, write_f)

            with open("Database/cache.json", "w") as write_f:
                json.dump(self.cache, write_f)

        else:
            if self.statistic["head"]["visualisation_mode"] == 2 and message.attachments != []:
                await message.remove_reaction(loading_emoji(), message.guild.me)
                await message.add_reaction(agree_emoji())
                await asyncio.sleep(3)
                await message.remove_reaction(agree_emoji(), message.guild.me)

    @commands.command()
    async def get_stat(self, ctx: commands.Context, _type="default", numb=-1):
        _type_aliases_v1 = ["detail", "d", "more", "m"]
        embed = discord.Embed(colour=discord.Colour.blurple())
        if _type == "default":
            embed.title = "Сводка"

            embed.add_field(name="Проанализированных файлов:", value=self.statistic["head"]["counter"], inline=False)
            embed.add_field(name="Подозрительных из них:", value=self.statistic["head"]["auto_crash_content"],inline=False)
            embed.add_field(name="Активный режим:", value=self.statistic["head"]["active_mode"], inline=False)
            embed.add_field(name="Режим отображения прогресса:", value=self.statistic["head"]["visualisation_mode"], inline=False)
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
                        activity=discord.Activity(type=discord.ActivityType.playing, name='Филтьрую опасный контент'))
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

            elif option in ["visualisation_mode", "visualisation", "v"]:
                if int(value) >= 0 and int(value) <= 2:
                    self.statistic["head"]["visualisation_mode"] = int(value)
                else:
                    raise commands.BadArgument

            elif option in ["cache_add", "ca"]:
                self.cache["black_listed_links"].append(value)

            elif option in ["cache_add", "ca"]:
                try:
                    self.cache["black_listed_links"].remove(value)
                except ValueError:
                    ctx.send(f"Значение {value} не найдено в кеше")

            with open("Database/Statistic.json", "w") as write_f:
                json.dump(self.statistic, write_f)

            with open("Database/cache.json", "w") as write_f:
                json.dump(self.cache, write_f)

        except Exception as error:
            await ctx.send(f"Ошибка: {error}")


def setup(bot):
    bot.add_cog(AntiCrashAttachments(bot))
