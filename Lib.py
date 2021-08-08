import discord
import asyncio
import asqlite
import random
import time
import json
import re

from discord.ext import commands
import types


def Config():
    with open('Config.json', 'r') as read_file:
        return json.load(read_file)


def Lang():
    with open('Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


with open("Database/cache.json", "rb") as read_f:
    cache = json.load(read_f)


config = Config()
lang = Lang()


bot = commands.Bot(command_prefix=config['prefix'],
                   intents=discord.Intents(guilds=True, messages=True, typing=False, emojis=True, members=True))
bot.owner_ids = [500020124515041283]

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
    return ctx.author.id in bot.owner_ids


def is_developer_2fa(ctx):
    with open("Database/cache.json", "rb") as read_c:
        cache = json.load(read_c)
    if cache["session"]["last_action_unix"] is not None and time.time() - cache["session"]["last_action_unix"] <= 300:
        cache["session"]["last_action_unix"] = time.time()
        with open("Database/cache.json", "w") as write_f:
            json.dump(cache, write_f)
        return ctx.author.id in bot.owner_ids and cache["session"]["is_session"] and ctx.guild.id == cache["session"]["guild_id"]
    else:
        Session_close(ctx)
        return False


def is_Moderator(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.manage_guild


def is_Admin(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.administrator


def random_base32(length=16, random_=random.SystemRandom(),
                  chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"):

    return ''.join(random_.choice(chars) for i in range(length))


def Session_close(ctx: commands.Context = None):
    print(int(cache["session"]["guild_id"]),int(ctx.guild.id) , int(cache["session"]["guild_id"]) == int(ctx.guild.id))
    if int(cache["session"]["guild_id"]) == int(ctx.guild.id):
        cache["session"]["is_session"] = False
        cache["session"]["guild_id"] = None
        cache["session"]["last_action_unix"] = None
        with open("Database/cache.json", "w") as write_f:
            json.dump(cache, write_f)
        return True
    else:
        return False


async def get_guild_language(ctx):
    return "ru"

async def get_db():
    async with asqlite.connect('Database/Data.db') as DB:
        return DB

async def db_get_guild(id_):
    async with DB.cursor() as curr:
        await curr.execute(f"SELECT * FROM guilds WHERE id = {id_}")
        guild_raw = tuple(await curr.fetchone())
        if guild_raw:
            guild = types.Guild()
            guild.id = guild_raw[0]
            guild.name = guild_raw[1]
            guild.mode = guild_raw[2]
            guild.mute_role_id = guild_raw[3]
            guild.lang = guild_raw[4]
            guild.flags = guild_raw[5]
            return guild
        else:
            return None

async def db_push_guild(guild:types.Guild):
    async with DB.cursor() as curr:
        try:
            await curr.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?);", (guild.id,
                                                                                      guild.name,
                                                                                      guild.mode,
                                                                                      guild.mute_role_id,
                                                                                      guild.lang,
                                                                                      guild.flags))
        except Exception as e:
            print(e)
        else:
            await DB.commit()



DB: asqlite.Connection = asyncio.run(get_db())
