import logging
import random
from datetime import datetime
import asyncio

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from core.misc import dp
from modules.elka.aiogram_ext import set_message_reaction, AVAILABLE_MESSAGE_REACTIONS

logger = logging.getLogger("assistant-bot.elka")
logging.basicConfig(
    format="%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s", level=logging.DEBUG
)


class ElkaMiddleware(BaseMiddleware):
    def __init__(self):
        super(ElkaMiddleware, self).__init__()

    async def on_pre_process_message(self, m: types.Message, data: dict):
        if m.chat.type in ("group", "supergroup"):
            elka_data = data.get("chat", {}).get("elka", {})
        else:
            elka_data = data.get("user", {}).get("elka", {})

        if elka_data:
            # try:
            emoji = elka_data.get("emoji", "random")
            if emoji == "random":
                emoji = random.choice(AVAILABLE_MESSAGE_REACTIONS)
            try:
                asyncio.create_task(
                    set_message_reaction(m.bot, m.chat.id, m.message_id, emoji, elka_data.get("effects", False))
                )
            except Exception as e:
                logger.exception(f"Unable to set reaction in chat {m.chat.id}", exc_info=True)


dp.middleware.setup(ElkaMiddleware())
