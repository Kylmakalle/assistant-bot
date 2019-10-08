from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from aiogram.utils.markdown import hlink, hbold

from core.misc import dp, mp, bot


@dp.message_handler(lambda m: m.chat.username == 'ru2chhw' and m.message_id == 3999999)
async def watch_get(m: types.Message, user: dict, chat: dict):
    # get = await bot.send_message(m.chat, text=hbold('GET /hw/ {}'.format(m.message_id + 1)))
    get = await bot.send_message(m.chat.id, text=hbold('🎉 GET /hw/ 4️⃣0️⃣0️⃣0️⃣0️⃣0️⃣0️⃣'))
    try:
        await bot.pin_chat_message(m.chat.id, get.message_id, disable_notification=False)
    except:
        pass

    await bot.send_message(94026383, text='GET @{} {}'.format(m.chat.username, hlink(str(get.message_id),
                                                                                     'https://t.me/{}/{}'.format(
                                                                                         m.chat.username,
                                                                                         get.message_id))))
    SkipHandler()
