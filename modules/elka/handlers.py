import asyncio
import logging
from aiogram import types

from core.misc import dp, mp, bot
from core.db import db
from modules.admin.utils import can_user_ban


@dp.message_handler(commands=["elka", "tree"], state="*")
async def cmd_elka(m: types.Message, user: dict, chat: dict):
    if m.chat.type in ("group", "supergroup"):
        try:
            user_request = await bot.get_chat_member(chat["id"], m.from_user.id)
        except Exception:
            await m.reply("Не могу получить информацию о юзере.")
            return

        if not can_user_ban(user_request, user):
            await m.answer("Гирлянда только для взрослых!")
            return

        elka_data = chat.get("elka", {})
    else:
        elka_data = user.get("elka", {})

    _, args = m.get_full_command()
    args = args.split()

    if not elka_data and not args:
        await m.reply(
            """Включает ёлку в чате и реагирует на новые сообщения.
`/elka <emoji> [effects]`
Эмоджи может быть `random` или один из [доступных](https://core.telegram.org/bots/api#reactiontypeemoji).
Параметр `effects` включает объемные анимации.

Примеры:
`/elka random`
`/elka 🎄 effects`
`/elka effects`
""",
            parse_mode=types.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    args_len = len(args)
    if args_len == 0:
        # removing
        if m.chat.type in ("group", "supergroup"):
            collection = db.chats
        else:
            collection = db.users
        await collection.update_one({"_id": user["_id"]}, {"$unset": {"elka": 1}})
        await m.reply("Ёлочка больше не горит 😢")
        return
    elif args_len == 1:
        if args[0] == "random":
            elka_data = {
                "emoji": "random",
            }
        elif args[0] == "effects":
            elka_data = {"effects": True}
        # Just emoji
        else:
            elka_data = {"emoji": args[0]}
    elif args_len == 2:
        elka_data = {"emoji": args[0], "effects": True}

    await m.answer("Раз")
    await asyncio.sleep(1)
    await m.answer("Два")
    await asyncio.sleep(1)
    await m.answer("Три")
    await asyncio.sleep(1)

    if m.chat.type in ("group", "supergroup"):
        collection = db.chats
    else:
        collection = db.users
    await collection.update_one({"_id": m.chat.id}, {"$set": {"elka": elka_data}})

    await m.answer("Ёлочка, гори!")
    await m.answer("🎄")
