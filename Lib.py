import discord
from datetime import datetime
from discord.ext import commands
import json
import sqlite3
from sys import version_info
import re


def Config():
    with open('Config.json', 'r') as read_file:
        return json.load(read_file)


def Lang():
    with open('Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


config = Config()
lang = Lang()

bot = commands.Bot(command_prefix=config['prefix'],
                   intents=discord.Intents(guilds=True, messages=True, typing=False, emojis=True, members=True))
console_log = 830490410778099752


def developer():
    return bot.get_user(config["devID"])


def convert_to_member(value):
    print(value)
    return value


def convert_to_channel(value):
    try:
        channelid = re.sub("[^0-9]", "", str(value))
        channel = bot.get_channel(int(channelid))
    except:
        channel = None
    return channel


def convert_to_role(guild, value):
    try:
        roleid = re.sub("[^0-9]", "", str(value))
        role = guild.get_role(int(roleid))
    except:
        role = None
    return role


def agree_emoji():
    return bot.get_emoji(764938637862371348)


def warning_emoji():
    return bot.get_emoji(776432019940573244)


def disagree_emoji():
    return bot.get_emoji(837961320107212810)


def loading_emoji():
    return bot.get_emoji(830796791837491210)


def is_developer(ctx):
    return ctx.author.id == config["devID"]


def is_Moderator(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.manage_guild


def is_Admin(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.administrator


async def get_guild_language(ctx):
    return "ru"
