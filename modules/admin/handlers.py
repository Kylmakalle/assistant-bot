from datetime import timedelta

from aiogram import types
from aiogram.utils import exceptions
from aiogram.utils.markdown import hbold, hitalic

from core.db import db, ReturnDocument
from core.log import log
from core.misc import bot, dp, mp
from core.stats import StatsEvents
from modules.captcha_button.handlers import add_log
from modules.voteban.consts import voter, LogEvents, get_admin_report_response
from modules.voteban.views import render_voteban_kb, screen_name
from private_modules.autoban.utils import get_user_id


@dp.message_handler(lambda m: (types.ChatType.is_group_or_super_group and m.reply_to_message),
                    commands=['kick'], commands_prefix='!/#')
async def cmd_kick_reply(m: types.Message, user: dict, chat: dict):
    kick_user = m.reply_to_message.from_user
    try:
        user_request = await bot.get_chat_member(chat['id'], m.from_user.id)
    except:
        await m.reply('Не могу получить информацию о юзере.')
        return

    if (user_request.is_admin() or user.get('status', 0) >= 3) and not kick_user.is_bot:
        kick_user = kick_user.to_python()

        try:
            await bot.kick_chat_member(chat['id'], kick_user['id'])
            await bot.unban_chat_member(chat['id'], kick_user['id'])
        except:
            pass

        await bot.send_message(chat['id'], 'Пользователь кикнут. Спасибо за свободное общение!',
                               reply_to_message_id=m.reply_to_message.message_id)

        await add_log(chat['id'], kick_user['id'], LogEvents.KICK, by=m.from_user.id)
        await log(event=LogEvents.KICK, chat=chat, user=kick_user, message_id=m.message_id, admin=user)
        await mp.track(m.from_user.id, StatsEvents.ADMIN_BAN, m)
    else:
        if m.from_user.id == kick_user.id:
            await m.reply("Ну ты сам напросился")
            try:
                await bot.kick_chat_member(chat['id'], kick_user['id'])
                await bot.unban_chat_member(chat['id'], kick_user['id'])
            except:
                pass
            return

        if kick_user.is_bot:
            if kick_user.id == (await bot.me).id:
                await m.reply('Сам себя кикни.')
            else:
                await m.reply('Ой да ладно тебе, это очередной тупой бот.')
            return

        try:
            user_in_chat = await bot.get_chat_member(chat['id'], kick_user.id)
        except:
            await m.reply('Не могу получить информацию о юзере.')
            return

        if user_in_chat.status == types.ChatMemberStatus.KICKED:
            await m.reply('Пользователя нет в чате.')
            return

        if user_in_chat.is_admin() or user.get('status', 0) >= 3:
            await m.reply("Слыш")
            return


@dp.message_handler(lambda m: (types.ChatType.is_group_or_super_group and not m.reply_to_message),
                    commands=['kick'], commands_prefix='!/#')
async def cmd_kick(m: types.Message, user: dict, chat: dict):
    await m.reply(
        'Эта команда работает только ответом на сообщение.\nЧтобы она работала по-другому, надо сделать Pull request...')


@dp.message_handler(lambda m: (types.ChatType.is_group_or_super_group and not m.reply_to_message),
                    commands=['ban'], commands_prefix='!/#')
async def cmd_ban_text(m: types.Message, user: dict, chat: dict):
    try:
        user_request = await bot.get_chat_member(chat['id'], m.from_user.id)
    except:
        await m.reply('Не могу получить информацию о юзере.')
        return
    if user_request.is_admin() or user.get('status', 0) >= 3:
        uid = await get_user_id(m)
        if uid != (await bot.get_me()).id:
            if uid:
                try:
                    await bot.kick_chat_member(chat['id'], uid)
                except:
                    pass

                ban_user = await db.users.find_one({'id': uid})

                await m.reply('Пользователь был забанен. Спасибо!')
                await add_log(chat['id'], uid, LogEvents.BAN, by=m.from_user.id)
                await log(event=LogEvents.BAN, chat=chat, user=ban_user, message_id=m.message_id, admin=user)
                await mp.track(m.from_user.id, StatsEvents.ADMIN_BAN, m)
            else:
                await m.reply('Такой тут не пробегал')
    else:
        await m.reply('Не-не ¯\_(ツ)_/¯')
