from loguru import logger

from pyjoibot import discord

if __name__ == "__main__":
    discord.bot.run(discord.config.TOKEN)
