import logging
import random
from datetime import datetime

from aiogram import types
from aiogram.contrib.middlewares.logging import LoggingMiddleware  # noqa: F401
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.markdown import quote_html, hlink

from core.config import allowed_chats
from core.db import db, ReturnDocument
from core.misc import dp

logger = logging.getLogger("assistant-bot.base")
logging.basicConfig(
    format="%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s", level=logging.DEBUG
)


async def update_user(from_user, update_visit=True):
    if not from_user.is_bot:
        user = await db.users.find_one({"id": from_user.id})

        if not user:
            from_user = from_user.to_python()

            user = from_user
            user.update({"_id": from_user["id"]})
            if user.get("first_name"):
                user["first_name"] = quote_html(user["first_name"])
            if user.get("last_name"):
                user["last_name"] = quote_html(user["last_name"])
            if update_visit:
                user.update({"last_visit": datetime.utcnow()})
            await db.users.insert_one(user)
        else:
            from_user = from_user.to_python()
            if "last_name" not in from_user:
                from_user["last_name"] = None
            if "username" not in from_user:
                from_user["username"] = None
            if from_user.get("first_name"):
                from_user["first_name"] = quote_html(from_user["first_name"])
            if from_user.get("last_name"):
                from_user["last_name"] = quote_html(from_user["last_name"])
            if update_visit:
                from_user.update({"last_visit": datetime.utcnow()})
            usr = {"$set": from_user}
            user = await db.users.find_one_and_update(
                {"_id": user["id"]}, usr, upsert=True, return_document=ReturnDocument.AFTER
            )
    else:
        user = {}
    return user


async def update_chat(from_chat):
    chat = await db.chats.find_one({"id": from_chat.id})

    if not chat:
        chat = from_chat.to_python()
        chat["title"] = quote_html(chat["title"])
        c = {"_id": chat["id"]}
        chat.update(c)

        await db.chats.insert_one(chat)
    else:
        # I don't care about chat title, really, even username
        pass

    return chat


class UpdatesLoggerMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self):
        super(UpdatesLoggerMiddleware, self).__init__()

    async def on_pre_process_update(self, update: types.Update, data: dict):
        u = update.to_python()
        # pprint(u)
        u.update({"_id": u["update_id"]})
        await db.updates.insert_one(u)

        if update.callback_query:
            from_user = update.callback_query.from_user
            from_chat = update.callback_query.message.chat
        elif update.message:
            from_user = update.message.from_user
            from_chat = update.message.chat
        elif update.edited_message:
            from_user = update.edited_message.from_user
            from_chat = update.edited_message.chat
        else:
            from_user = None
            from_chat = None

        if from_user:
            data["user"] = await update_user(from_user)

        if from_chat and from_chat.type == "supergroup":
            chat = await update_chat(from_chat)

            data["chat"] = chat

    async def on_pre_process_message(self, m: types.Message, data: dict):
        if m.content_type == types.ContentType.NEW_CHAT_MEMBERS:  # noqa: E721
            new_chat_members = []
            for new_chat_member in m.new_chat_members:
                if not new_chat_member.is_bot:
                    new_chat_members.append(await update_user(new_chat_member, update_visit=False))

            data["new_chat_members"] = new_chat_members
        from_user = m.from_user
        from_chat = m.chat
        user = await db.users.find_one({"id": from_user.id})
        data["user"] = user
        chat = await db.chats.find_one({"id": from_chat.id})
        data["chat"] = chat
        # await mp.track(m.from_user.id, 'message', m)

    async def on_pre_process_edited_message(self, m: types.Message, data: dict):
        from_user = m.from_user
        from_chat = m.chat
        user = await db.users.find_one({"id": from_user.id})
        data["user"] = user
        chat = await db.chats.find_one({"id": from_chat.id})
        data["chat"] = chat

    async def on_pre_process_callback_query(self, c: types.CallbackQuery, data: dict):
        from_user = c.from_user
        from_chat = c.message.chat
        user = await db.users.find_one({"id": from_user.id})
        data["user"] = user
        chat = await db.chats.find_one({"id": from_chat.id})
        data["chat"] = chat
        # await mp.track(c.from_user.id, 'callback', c)


class PrivateBotMiddleware(BaseMiddleware):
    contact_required_text = (
        f"🔶 <b>Напоминаю</b>, что лучший чат про железо, ПК и технологии это {hlink('@ru2chhw', 'https://t.me/ru2chhw')}.\n\n"
        + "Этот чат: {chat_title} #chat{chat_id}\n"
        + "Админ бота: @Kylmakalle"
    )

    def __init__(self):
        super(PrivateBotMiddleware, self).__init__()

    async def on_pre_process_message(self, m: types.Message, data: dict):
        if m.chat.type in ("group", "supergroup"):
            if (m.chat.username or "").lower() not in allowed_chats and str(m.chat.id) not in allowed_chats:
                if random.random() >= 0.95:
                    try:
                        await dp.bot.send_message(
                            m.chat.id,
                            self.contact_required_text.format(chat_title=m.chat.title, chat_id=abs(m.chat.id)),
                        )

                    except Exception:
                        pass
                    raise CancelHandler()


# logging_ms = dp.middleware.setup(LoggingMiddleware())
update_logger = dp.middleware.setup(UpdatesLoggerMiddleware())
private_bot = dp.middleware.setup(PrivateBotMiddleware())
