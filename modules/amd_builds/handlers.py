from aiogram.utils.markdown import hitalic, hbold
from aiogram import types
from modules.voteban.views import screen_name

from core.misc import bot, dp, mp
from modules.amd_builds.utils import get_build
from modules.amd_builds.consts import StatsEvents

import random

init_msgs = (
    'Звоним Лизе Су',
    'Просим Петровича помочь',
    'Спайк разгоняет память',
    'Надо только подождать',
    'Что-же вам на Интуле то не сидится',
    'Ждем заказ из ДНС',
    'Придумайте новые фразы плз',
    'yasobe.ru/na/petrovi4_s_dr ',
    'Еманло выпрямляет ножки',
    '"Только бы не Гигабит"',
    'Раскрываем потанцевал'
)

error_msgs = (
    '{user}, <b>твою сборку задержали на таможне</b>',
    '{user}, <b>накопленных с обедов денег не хватило на AMD сборку</b>',
    '<b>Ошибка, сори</b>',
    '<b>Автобэкап не выполнен</b>'
)

build_template = '<a href="{link}">&#8203;</a><b>{title}</b>\nu/{user}\n<a href="{reddit_url}">Reddit</a>'


@dp.message_handler(commands=['amd', 'build', 'reddit'])
async def cmd_amd_build(m: types.Message, user: dict, chat: dict):
    if not (m.chat.username in ('ru2chhw', 'Kylmakalle',) or m.chat.id in (-1001108829366,)):
        await m.reply('Эта команда доступна только в @ru2chhw')
        return

    sent = await m.reply(hitalic(random.choice(init_msgs) + '...'), reply=False)

    try:
        build = await get_build(amount=150)
    except:
        build = None

    if not build:
        await sent.edit_text(random.choice(error_msgs).format(user=screen_name(m.from_user, True)))

        await mp.track(m.from_user.id, StatsEvents.AMDBUILD_ERROR, m)
    else:
        await sent.edit_text(
            build_template.format(link=build['photo'], title=build['title'], user=screen_name(m.from_user, True),
                                  reddit_url=build['reddit_url']))

        await mp.track(m.from_user.id, StatsEvents.AMDBUILD, m)

    try:
        await m.delete()
    except:
        pass
