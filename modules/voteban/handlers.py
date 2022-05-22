import logging
from datetime import datetime
from datetime import timedelta
from io import BytesIO

from aiogram import types
from aiogram.utils import exceptions
from aiogram.utils.json import json
from aiogram.utils.markdown import hbold, hitalic
from bson.json_util import _json_convert

from core.db import db, ReturnDocument
from core.log import log
from core.misc import bot, dp, mp
from core.stats import StatsEvents
from modules.admin.handlers import cmd_tempban, ban_sender_chat
from modules.admin.utils import get_time_args, can_user_ban
from modules.captcha_button.handlers import add_log
from modules.voteban.consts import voter, LogEvents, get_admin_report_response
from modules.voteban.views import render_voteban_kb, screen_name


async def get_voteban(chat_id: int, user_id: int) -> dict:
    return await db.votebans.find_one({"user_id": user_id, "chat_id": chat_id, "active": True})


async def update_voteban(chat_id: int, user_id: int, u: dict) -> dict:
    return await db.votebans.find_one_and_update(
        {"user_id": user_id, "chat_id": chat_id, "active": True}, u, return_document=ReturnDocument.AFTER
    )


async def cmd_fun_report(m: types.Message, user: dict, chat: dict):
    try:
        await m.delete()
    except Exception:
        pass
    await bot.send_message(m.chat.id, get_admin_report_response(), reply_to_message_id=m.reply_to_message.message_id)


@dp.message_handler(
    lambda m: (types.ChatType.is_group_or_super_group and m.reply_to_message),
    commands=["report", "ban", "voteban"],
    commands_prefix="!/#",
)
async def cmd_report(m: types.Message, user: dict, chat: dict):
    if m.reply_to_message.sender_chat and await ban_sender_chat(m):
        return
    vote_user = m.reply_to_message.from_user
    try:
        user_request = await bot.get_chat_member(chat["id"], m.from_user.id)
    except Exception:
        await m.reply("Не могу получить информацию о юзере.")
        return

    if can_user_ban(user_request, user) and not vote_user.is_bot:
        check_cmd = m.text.replace("!", "").replace("/", "").replace("#", "")
        if (check_cmd or "").lower().startswith("report"):
            await cmd_fun_report(m, user, chat)
            return
        _, _, msg_args = m.text.partition(" ")
        if (check_cmd or "").lower().startswith("ban") and msg_args and get_time_args(msg_args)[0]:
            await cmd_tempban(m, user, chat)
            return
        vote_user = vote_user.to_python()
        vote_user.update({"spamer": 1.0})
        usr = {"$set": vote_user}
        await db.users.find_one_and_update(
            {"_id": vote_user["id"]}, usr, upsert=True, return_document=ReturnDocument.AFTER
        )
        await update_voteban(
            chat["id"],
            vote_user["id"],
            {"$set": {"active": False, "confirmed": True, "closed_datetime": datetime.utcnow()}},
        )
        try:
            await bot.kick_chat_member(chat["id"], vote_user["id"])
        except Exception:
            pass
        await m.reply(f"Пользователь {screen_name(vote_user, True)} был забанен и помечен как спамер. Спасибо!")
        try:
            await bot.delete_message(m.chat.id, m.reply_to_message.message_id)
        except Exception:
            pass
        await add_log(chat["id"], vote_user["id"], LogEvents.BAN, by=m.from_user.id)
        await log(event=LogEvents.BAN, chat=chat, user=vote_user, message_id=m.message_id, admin=user)
        await mp.track(m.from_user.id, StatsEvents.ADMIN_BAN, m)
    else:
        if m.from_user.id == vote_user.id:
            if (
                user_request.can_send_media_messages
                and user_request.can_send_other_messages
                and user_request.can_add_web_page_previews
            ):
                await m.reply("Ну ты сам напросился")
                try:
                    await bot.restrict_chat_member(chat["id"], vote_user.id, until_date=m.date + timedelta(seconds=35))
                except Exception:
                    pass
                await mp.track(m.from_user.id, StatsEvents.SELF_BAN, m)
            else:
                await m.reply("Піймав на обхід бана, до вас вже виїхали")
            return

        if vote_user.is_bot:
            if vote_user.id == (await bot.me).id:
                if "report" in m.text:
                    await m.reply("Сам себя зарепорти.")
                elif "ban" in m.text:
                    await m.reply("Сам себя забань.")
            else:
                await m.reply("Ой да ладно тебе, это очередной тупой бот.")
            return

        try:
            user_in_chat = await bot.get_chat_member(chat["id"], vote_user.id)
        except Exception:
            await m.reply("Не могу получить информацию о юзере.")
            return

        if user_in_chat.status == types.ChatMemberStatus.KICKED:
            await m.reply("Пользователя нет в чате.")
            return

        if can_user_ban(user_in_chat, user):
            await m.reply(f"{hitalic('Баню пользователя')} {screen_name(m.from_user)} =)")
            return

        voteban = await get_voteban(chat["id"], vote_user.id)
        new_vb = False
        if not voteban:
            new_vb = True
            voteban = {
                "user_id": vote_user.id,
                "chat_id": chat["id"],
                "votes": [{"user_id": user["id"]}],
                "active": True,
                "active_datetime": datetime.utcnow(),
            }
            await db.votebans.insert_one(voteban)

        kb = render_voteban_kb(voteban)
        vb_msg = await bot.send_message(
            chat["id"],
            f"{hbold('Voteban')} для {screen_name(vote_user)}"
            + "\n\n"
            + f"{hbold('Внимание!')} Ложные воутбаны влияют на значимость ваших репортов.",
            reply_to_message_id=m.reply_to_message.message_id,
            reply_markup=kb,
        )
        if new_vb:
            await log(
                event=LogEvents.VOTEBAN,
                chat=chat,
                user=user,
                message_id=vb_msg.message_id,
                text_kwargs={"vote_for": f"{screen_name(vote_user.to_python())} [#id{vote_user.id}]"},
            )
        await mp.track(m.from_user.id, StatsEvents.VOTEBAN_CALL, m)


@dp.callback_query_handler(voter.filter())
async def btn_vote(c: types.CallbackQuery, user: dict, chat: dict, callback_data: dict):
    voteban = await get_voteban(int(callback_data["chat_id"]), int(callback_data["user_id"]))
    try:
        user_request = await bot.get_chat_member(chat["id"], c.from_user.id)
    except Exception:
        return
    if can_user_ban(user_request, user):
        if voteban["active"]:
            vote_user = await db.users.find_one({"id": int(callback_data["user_id"])})
            vote_user.update({"spamer": 1.0})
            usr = {"$set": vote_user}
            await db.users.find_one_and_update(
                {"_id": vote_user["id"]}, usr, upsert=True, return_document=ReturnDocument.AFTER
            )
            await update_voteban(
                chat["id"],
                vote_user["id"],
                {"$set": {"active": False, "confirmed": True, "closed_datetime": datetime.utcnow()}},
            )
            try:
                await bot.kick_chat_member(int(callback_data["chat_id"]), int(callback_data["user_id"]))
            except Exception:
                await c.answer(text="Возникла ошибка при попытке забанить пользователя.", show_alert=True)
                return
            text = "Воутбан завершён, пользователь был забанен."
            await c.message.edit_text(text=c.message.html_text + "\n\n" + hitalic(text))
            await c.answer(text="Пользователь был забанен!")
            await add_log(chat["id"], vote_user["id"], LogEvents.BAN, by=c.from_user.id)
            await log(event=LogEvents.BAN, chat=chat, user=vote_user, message_id=c.message.message_id, admin=user)
            await mp.track(c.from_user.id, StatsEvents.VOTEBAN_CONFIRM, c)
        else:
            if voteban["confirmed"]:
                text = "Воутбан завершён, пользователь был забанен."
            else:
                text = "Воутбан завершён, пользователь не был забанен."

            await c.answer(text=text, show_alert=True)
            await c.message.edit_text(text=c.message.html_text + "\n\n" + hitalic(text))
    else:
        if voteban["active"]:
            user_voted = bool([vote for vote in voteban["votes"] if vote["user_id"] == user["id"]])

            if user_voted:
                command = "$pull"
            else:
                command = "$push"

            u = {command: {"votes": {"user_id": user["id"]}}}

            voteban = await update_voteban(voteban["chat_id"], voteban["user_id"], u)
            kb = render_voteban_kb(voteban)

            try:
                await bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=kb)
            except exceptions.MessageNotModified:
                pass
            if user_voted:
                answer_text = "Голос убран"
                await mp.track(c.from_user.id, StatsEvents.VOTEBAN_UNVOTE, c)
            else:
                answer_text = "Вы проголосовали за бан"
                await mp.track(c.from_user.id, StatsEvents.VOTEBAN_VOTE, c)
            await c.answer(text=answer_text)
        else:
            if voteban["confirmed"]:
                text = "Воутбан завершён, пользователь был забанен."
            else:
                text = "Воутбан завершён, пользователь не был забанен."

            await c.answer(text=text, show_alert=True)
            await c.message.edit_text(text=c.message.html_text + "\n\n" + hitalic(text))


@dp.message_handler(
    # /hw/
    lambda m: m.chat.id == "-1001108829366" or m.from_user.username == "Kylmakalle",
    commands=["export_votebans"],
    commands_prefix="!/#",
)
async def cmd_export_votebans(m: types.Message, user: dict, chat: dict):
    start_message = await m.reply(hitalic("Начинаю экспорт..."))
    vbs = await db.votebans.find({"chat_id": -1001086103845}).to_list(None)
    converted_vbs = _json_convert(vbs)

    try:
        with BytesIO() as file:
            file.write(json.dumps(converted_vbs, ensure_ascii=False).encode())
            file.name = "hw_votebans.json"
            file.seek(0)
            await m.reply_document(file)
    except Exception:
        logging.exception("Error exporting votebans")
        await m.reply("Неизвестная ошибка при экспорте")

    try:
        await start_message.delete()
    except Exception:
        pass
