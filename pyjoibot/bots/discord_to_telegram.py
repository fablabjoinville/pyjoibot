import asyncio
from collections import defaultdict
from typing import Optional

import discord
import telegram
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from loguru import logger
from slugify import slugify

from .config import (DISCORD_CHANNEL_FROM, DISCORD_TOKEN, TELEGRAM_GROUP_ID,
                     TELEGRAM_TOKEN)
from .utils import cmdlog

bot_discord = Bot(command_prefix="!", intents=discord.Intents.all())
bot_telegram = telegram.Bot(token=TELEGRAM_TOKEN)


@bot_discord.event
async def on_message(message):

    if message.channel.name in DISCORD_CHANNEL_FROM.split(","):
        logger.debug(f"## Message {message}")
        logger.debug(f"## Telegram Groups {type(TELEGRAM_GROUP_ID)}")

        send_message = """ 
        ## Nova mensagem no canal do Discord:
        {content}  
        --  Enviado por: {author} do canal {channel} do servidor {server}
        --  Para fazer parte do servidor acesse: https://discord.gg/F7WWtt49hh

        """.format(
            content=message.content,
            author=message.author.name,
            channel=message.channel.name,
            server=message.guild.name,
        )

        for group in TELEGRAM_GROUP_ID.split(","):
            logger.debug(f"## Group {message}")
            bot_telegram.send_message(chat_id=group, text=send_message)

    await bot_discord.process_commands(message)


@bot_discord.event
async def on_error(event, *args, **kwargs):
    """Don't ignore the error, causing Sentry to capture it."""
    raise


@bot_discord.command()
@cmdlog
async def echo(ctx, *args):
    msg = " ".join(args)
    await ctx.channel.send(msg)


@bot_discord.command()
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


def run() -> None:
    logger.debug("Start bot discord to telegram")
    bot_discord.run(DISCORD_TOKEN)
