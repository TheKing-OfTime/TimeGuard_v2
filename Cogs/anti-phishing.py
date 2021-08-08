import asyncio
import discord
from discord.ext import commands
from Lib import is_developer, disagree_emoji, loading_emoji, agree_emoji, db_get_guild




class AntiPhishing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        guild = await db_get_guild(message.guild.id)
        m_content = []
        if guild.flags & 1:
            for mess in message.author.history(limit=2):
                m_content.append(mess.content)
            if m_content[0] == m_content[1] and len(m_content[0]) > 15:
                await asyncio.sleep(3)
                for mess in message.author.history():
                    if mess.content == m_content[0]:
                        await mess.delete()
                    else:
                        break
            else:
                return
        else:
            return

def setup(bot):
    bot.add_cog(AntiPhishing(bot))
