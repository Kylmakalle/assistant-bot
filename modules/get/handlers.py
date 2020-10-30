from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from aiogram.utils.markdown import hlink, hbold, hide_link

from core.misc import dp, mp, bot


@dp.message_handler(lambda m: m.chat.username == 'ru2chhw' and m.message_id == 3999999)
async def watch_get(m: types.Message, user: dict, chat: dict):
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


@dp.message_handler(lambda m: (m.chat.username == 'ru2chhw' and m.message_id == 5999999) or (
        m.from_user.id == 94026383 and m.chat.type == 'private' and m.text == '/get6kk'))
async def watch_get_six(m: types.Message, user: dict, chat: dict):
    pic_url = 'https://user-images.githubusercontent.com/24507532/97610210-a0decc00-1a25-11eb-9622-7b1e3536dfc0.png'
    get = await bot.send_message(m.chat.id, text=hide_link(pic_url) + hbold(
        '🎉 GET /hw/ 6️⃣0️⃣0️⃣0️⃣0️⃣0️⃣0️⃣') + '\n\n' + "Забавный факт - если поделить гет на 100, то получится цена RTX 3070!")
    try:
        await bot.pin_chat_message(m.chat.id, get.message_id, disable_notification=False)
    except:
        pass

    await bot.send_message(94026383, text='GET @{} {}'.format(m.chat.username, hlink(str(get.message_id),
                                                                                     'https://t.me/{}/{}'.format(
                                                                                         m.chat.username,
                                                                                         get.message_id))))
    SkipHandler()
