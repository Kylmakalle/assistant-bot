from asyncio import sleep, create_task
from datetime import datetime

from aiogram import types

from core.config import kick_delay
from core.db import db, ReturnDocument, ObjectId
from core.misc import bot, dp, mp
from core.stats import StatsEvents
from modules.captcha_button.consts import captcha_cb, LogEvents
from modules.captcha_button.utils import get_welcome_message, get_user_msgs_to_delete_date
from modules.voteban.views import screen_name


async def add_log(chat_id, user_id, event, **kwargs):
    log_dict = {"date": datetime.utcnow(), "event": event}
    if kwargs:
        log_dict.update(kwargs)
    return await db.log.find_one_and_update(
        dict(chat_id=chat_id, user_id=user_id),
        {"$push": {"log": log_dict}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )


async def get_user_captcha_passed(user_id, chat_id):
    return next(
        (
            item
            for item in (await db.log.find_one({"user_id": user_id, "chat_id": chat_id}) or {}).get("log", [])
            if item["event"] == LogEvents.CAPTCHA_PASSED
        ),
        None,
    )


async def kick_timer(chat_id, user, messages_to_delete):
    await sleep(kick_delay)
    captcha_passed_action = await get_user_captcha_passed(user["id"], chat_id)
    if not captcha_passed_action:
        await bot.ban_chat_member(chat_id, user["id"])
        await bot.unban_chat_member(chat_id, user["id"])
        await add_log(chat_id, user["id"], LogEvents.CAPTCHA_TIMEOUT)
        for message in messages_to_delete:
            try:
                await bot.delete_message(chat_id, message)
            except Exception:
                pass
        await mp.track(
            user["id"], StatsEvents.CAPTCHA_TIMEOUT, properties={"chat_id": chat_id, "chat_type": "supergroup"}
        )


async def try_delete_msg(chat_id, message_id):
    try:
        return await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_chat_members_handler(m: types.Message, user: dict, chat: dict, new_chat_members: list):
    kick_tasks = []
    delete_tasks = []
    for n_c_m in new_chat_members:
        # await add_log(chat['id'], n_c_m['id'], LogEvents.JOINED)
        captcha_passed_action = await get_user_captcha_passed(n_c_m["id"], m.chat.id)
        if not captcha_passed_action:
            challenge_id, welcome, kb = await get_welcome_message(n_c_m, chat["title"], m.message_id)
            welcome_msg = await bot.send_message(m.chat.id, welcome, reply_markup=kb)
            await bot.restrict_chat_member(
                m.chat.id,
                n_c_m["id"],
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            )
            await db.c_challenges.update_one({'_id': ObjectId(challenge_id)}, {'$set': {'welcome_msg': welcome_msg.to_python()}})
            passed_updates = await get_user_msgs_to_delete_date(
                m.chat.id, n_c_m["id"], int(m.date.timestamp()), m.message_id
            )
            for i in passed_updates:
                delete_tasks.append(create_task(try_delete_msg(chat["id"], i["message"]["message_id"])))
            kick_tasks.append(create_task(kick_timer(m.chat.id, n_c_m, [welcome_msg.message_id, m.message_id])))
            await mp.track(user["id"], StatsEvents.JOIN_CHAT, m)
        else:
            # User returned to chat
            pass
    for task in kick_tasks:
        await task


async def get_user_unrestrict_params(user_id, chat_id=None):
    # todo: Automated trust factor system
    return dict(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )


@dp.callback_query_handler(captcha_cb.filter())
async def captcha_cb_handler(c: types.CallbackQuery, user: dict, chat: dict, callback_data: dict):
    if int(callback_data["user_id"]) == c.from_user.id:
        challenge = await db.c_challenges.find_one({"_id": ObjectId(callback_data["challenge"]), "user_id": user["id"]})
        if challenge:
            if challenge["answer"] == callback_data["answer"]:
                unrestrict_params = await get_user_unrestrict_params(user["id"], chat["id"])
                await bot.restrict_chat_member(c.message.chat.id, c.from_user.id, **unrestrict_params)
                await add_log(c.message.chat.id, c.from_user.id, LogEvents.CAPTCHA_PASSED)
                text = f"Поприветствуем {screen_name(user)}!"
                await c.message.edit_text(text=text)
                await mp.track(user["id"], StatsEvents.CAPTCHA_PASSED, c)
            else:
                await c.answer(text="Ответ неверный! Пожалуйста, попробуйте еще раз!", show_alert=True)
                try:
                    await bot.delete_message(c.message.chat.id, c.message.message_id)
                except Exception:
                    pass
                try:
                    await bot.delete_message(c.message.chat.id, challenge["join_msg_id"])
                except Exception:
                    pass
                await bot.unban_chat_member(c.message.chat.id, c.from_user.id)
                await add_log(c.message.chat.id, c.from_user.id, LogEvents.CAPTCHA_ERROR)
                await mp.track(user["id"], StatsEvents.CAPTCHA_ERROR, c)
    else:
        await c.answer("Молодой человек, это не для Вас написано.", show_alert=True)
