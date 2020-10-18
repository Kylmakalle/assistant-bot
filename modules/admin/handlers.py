from datetime import datetime, timedelta

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
from modules.admin.utils import format_seconds
from private_modules.autoban.utils import get_user_id
from private_modules.autoban.consts import unban_cb
from durations import Duration
from durations.helpers import valid_duration

KICK_STICKERS = (
    # daykick
    'AgADVgIAArtXhwQ',
    'AgADVQIAArtXhwQ',
    'AgADVAIAArtXhwQ',
    'AgADUwIAArtXhwQ',

    # hw pack
    'AgADLgQAAjgzwQk',
    'AgADLwQAAjgzwQk',
    'AgADMAQAAjgzwQk'
)

KICK_PACKS = ('daykick',)


@dp.message_handler(lambda m: types.ChatType.is_group_or_super_group and m.reply_to_message
                              and (m.sticker.set_name in KICK_PACKS or m.sticker.file_unique_id in KICK_STICKERS),
                    content_types=['sticker'])
@dp.message_handler(lambda m: (types.ChatType.is_group_or_super_group and m.reply_to_message),
                    commands=['kick'], commands_prefix='!/#')
async def cmd_kick_reply(m: types.Message, user: dict, chat: dict):
    kick_user = m.reply_to_message.from_user
    try:
        user_request = await bot.get_chat_member(chat['id'], m.from_user.id)
    except:
        await m.reply('Не могу получить информацию о юзере.')
        return

    if (user_request.is_chat_admin() or user.get('status', 0) >= 3) and not kick_user.is_bot:
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

        if user_in_chat.is_chat_admin() or user.get('status', 0) >= 3:
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
    if user_request.is_chat_admin() or user.get('status', 0) >= 3:
        try:
            uid = await get_user_id(m)
        except:
            await m.reply('<b>Кавоо?</b>')
            return
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


@dp.message_handler(lambda m: (m.reply_to_message and types.ChatType.is_group_or_super_group),
                    commands=['tempban', 'tban', 'bant', 'tempb', 'разгон', 'разгонять'], commands_prefix="!/#")
async def cmd_tempban(m: types.Message, user: dict, chat: dict):
    try:
        user_request = await bot.get_chat_member(chat['id'], m.from_user.id)
    except:
        await m.reply('Не могу получить информацию о юзере.')
        return
    if not (user_request.is_chat_admin() or user.get('status', 0) >= 3):
        return await m.reply('Ты куда лезишь?')

    chat_id = chat['id']
    target_user_id = m.reply_to_message.from_user.id
    ban_user = await db.users.find_one({'id': target_user_id})

    command, _, msg_args = m.text.partition(' ')
    if msg_args:
        time_string = ''.join(msg_args)
        if valid_duration(time_string):
            duration = Duration(time_string)

            ban_seconds = duration.to_seconds()
            human_time = format_seconds(ban_seconds)
            try:
                await bot.restrict_chat_member(chat_id, target_user_id,
                                               until_date=datetime.utcnow() + timedelta(seconds=ban_seconds),
                                               can_send_messages=False)
            except Exception as e:
                return await m.reply('штото пошло не так :((')
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton('Unban', callback_data=unban_cb.new(
                chat_id=str(chat['id']),
                user_id=str(ban_user['id'])
            )))
            await add_log(chat_id, target_user_id, LogEvents.TEMPBAN, by=m.from_user.id)
            await log(event=LogEvents.TEMPBAN, chat=chat, user=ban_user, message_id=m.message_id, admin=user,
                      text_kwargs={'duration': human_time}, log_kwargs={'reply_markup': kb})
            await mp.track(m.from_user.id, StatsEvents.TEMPBAN, m)

            await m.reply(f'Пользователь пошёл разгонять память {hbold(human_time)}. Ждём с результатом!')
        else:
            return await m.reply('Я такие даты не понимаю')

    else:
        await m.reply('Ты что делаешь? Напиши !tempban 12h')
