import asyncio
from collections import defaultdict
from typing import Optional

import discord
import telegram
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from loguru import logger
from slugify import slugify

from .config import (
    DISCORD_CHANNEL_FROM,
    DISCORD_TOKEN,
    TELEGRAM_GROUP_ID,
    TELEGRAM_TOKEN,
)
from .utils import cmdlog

bot_discord = Bot(command_prefix="!", intents=discord.Intents.all())
bot_telegram = telegram.Bot(token=TELEGRAM_TOKEN)


@bot_discord.event
async def on_message(message):

    if message.channel.name in DISCORD_CHANNEL_FROM.split(","):
        for group in TELEGRAM_GROUP_ID.split(","):
            logger.debug(
                f"## Enviando mensagem do Discord: {message.channel.name} para Telegram: {group}"
            )

            send_message_telegram(group, message, header=True, footer=True)

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


def send_message_telegram(
    telegram_group, discord_message, header=False, footer=False
) -> None:
    if header:
        header = f"*\#\# Mensagem do Discord do canal _\#{discord_message.channel.name}_ no servidor _{discord_message.guild.name}_:*\n\n"
        bot_telegram.send_message(
            chat_id=telegram_group,
            text=header,
            parse_mode=telegram.ParseMode.MARKDOWN_V2,
        )

    bot_telegram.send_message(chat_id=telegram_group, text=discord_message.content)

    if footer:
        footer = (
            f"`enviado por: {discord_message.author.name}` \n\n Faça parte do servidor: [link](https://discord.gg/F7WWtt49hh)\."
            ""
        )
        bot_telegram.send_message(
            chat_id=telegram_group,
            text=footer,
            parse_mode=telegram.ParseMode.MARKDOWN_V2,
        )


def run() -> None:
    logger.debug("Start bot discord to telegram")
    bot_discord.run(DISCORD_TOKEN)
