# -*- coding: utf8 -*-

from Lib import bot, config
import os


if __name__ == '__main__':
    for cog in os.listdir("Cogs"):
        if cog.endswith(".py"):
            try:
                cog = f"Cogs.{cog.replace('.py', '')}"
                bot.load_extension(cog)
            except Exception as e:
                print(f"{cog} Can not be loaded")
                raise e
            else:
                print(f"{cog} has been successfully Loaded.")
bot.unload_extension("Cogs.dev_session")
bot.run(config["token"])

