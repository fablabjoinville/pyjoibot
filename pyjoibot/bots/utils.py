import asyncio
import functools

from datetime import datetime, timedelta
from loguru import logger


def cmdlog(f):
    @functools.wraps(f)
    async def wrapper(ctx, *args, **kwargs):
        logger.info(
            f"/{f.__name__} command trigger by user. user={ctx.message.author!r}"
        )
        await f(ctx, *args, **kwargs)

    return wrapper
