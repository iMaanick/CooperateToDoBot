import asyncio
import logging
import pprint
import time
import os
import asyncpg
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable


from aiogram.dispatcher.middlewares.base import BaseMiddleware


class DbMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.pool.Pool):
        super().__init__()
        self.pool = pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["pool"] = self.pool
        return await handler(event, data)
