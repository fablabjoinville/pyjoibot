import asyncio
import logging
import os
from collections import defaultdict
from typing import Optional

import telegram
from loguru import logger
from slugify import slugify

import discord
from discord.ext.commands import Bot
from discord.ext.tasks import loop

from .config import TELEGRAM_TOKEN
from .utils import cmdlog

bot = Bot(command_prefix="!", intents=discord.Intents.all())

bot_telegram = telegram.Bot(token=TELEGRAM_TOKEN)

@bot.event
async def on_message(message):
    # if not message.author.bot and message.content.lower() == "galvão?":
    #     await message.channel.send("Fala Tino!")

    # bot_telegram.send_message(chat_id='@pythonjoinville', text=message)
    logger.warning(message)

    await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    """Don't ignore the error, causing Sentry to capture it."""
    raise

@bot.command()
@cmdlog
async def echo(ctx, *args):
    msg = " ".join(args)
    await  ctx.channel.send(msg)

@bot.command()
@cmdlog
async def msg(ctx, *args):
    if len(args) < 2:
        logger.warning("missing destination message and message")
        await ctx.channel.send("!msg #canal mensagem a ser enviada")
        return

    if args[0].startswith("<#"):
        channel_id = int(args[0][2:-1])
        destination = discord.utils.get(ctx.guild.channels, id=channel_id)
    elif args[0].startswith("<@"):
        member_id = int(args[0][2:-1])
        destination = discord.utils.get(ctx.guild.members, id=member_id)
    else:
        logger.warning(f"Not a channel or user. args={args}")
        await ctx.channel.send(
            f"Não tem nenhuma pessoa ou canal com esse nome **{args[0]}** para enviar a mensagem"
        )
        return

    if not destination:
        logger.warning(
            f"Destination not found. destination={destination!r}, args={args!r}"
        )
        return

    message = " ".join(args[1:])
    logger.info(f"message sent. destination={destination}, message={message}")
    await destination.send(message)
