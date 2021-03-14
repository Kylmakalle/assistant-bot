from aiogram import types

from core.config import git_repository, bot_token
from core.misc import dp, mp, bot
from core.stats import StatsEvents

from core.config import clarifai_token
from modules.nsfw.functions import check_nsfw
from modules.nsfw.consts import MIME_TYPES


async def get_file_url(file_id):
    file = await bot.get_file(file_id)
    url = bot.get_file_url(file.file_path)
    return url


def get_check_url(message):
    file_id = None
    file_unique_id = None
    is_video = False
    if message.reply_to_message.photo:
        file_id = message.reply_to_message.photo[-1].file_id
        file_unique_id = message.reply_to_message.photo[-1].file_unique_id
    elif message.reply_to_message.animation:
        is_video = True
        file_id = message.reply_to_message.animation.file_id
        file_unique_id =  message.reply_to_message.animation.file_unique_id
    elif message.reply_to_message.video:
        is_video = True
        file_id = message.reply_to_message.video.file_id
        file_unique_id = message.reply_to_message.video.file_unique_id
    elif message.reply_to_message.video_note:
        is_video = True
        file_id = message.reply_to_message.video_note.file_id
        file_unique_id = message.reply_to_message.video_note.file_unique_id
    elif message.reply_to_message.document and message.reply_to_message.document.mime_type in MIME_TYPES.values():
        file_id = message.reply_to_message.document.file_id
        file_unique_id = message.reply_to_message.document.file_unique_id
        mime_type = message.reply_to_message.document.mime_type
        if 'video' in mime_type:
            is_video = True
    elif message.reply_to_message.sticker:
        file_id = message.reply_to_message.sticker.file_id
        file_unique_id = message.reply_to_message.sticker.file_unique_id

    return file_id, file_unique_id, is_video


@dp.message_handler(commands=['nsfw', 'sfw'], state='*')
async def cmd_nsfw(message: types.Message):
    if clarifai_token:
        if message.reply_to_message:
            file_id, file_unique_id, is_video = get_check_url(message)
            if not file_id:
                await message.reply('Неподдерживаемый тип медиа!')
                return

            await bot.send_chat_action(message.chat.id, 'typing')

            try:
                url = await get_file_url(file_id)
            except:
                await message.reply('Не могу получить информацию о медиа!')
                return

            try:
                result = await check_nsfw(url, file_unique_id, is_video=is_video, chat_id=message.chat.id)
            except Exception as e:
                await message.reply('Не могу проверить медиа!')
                return
            nsfw = result['nsfw']
            sfw = result['sfw']

            status = 'NSFW 🍓' if nsfw >= sfw else 'SFW 👌'
            percentage = nsfw if nsfw >= sfw else sfw
            await bot.send_message(message.chat.id,
                                   'Я на <code>{:.1%}</code> уверен, что это <b>{}</b>'.format(percentage,
                                                                                               status),
                                   parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        else:
            await message.reply('Ответь на сообщение с медиа!')
    else:
        await message.reply(f"Feature not implemented yet, stay tuned! {git_repository}")
    await mp.track(message.from_user.id, StatsEvents.NSFW, message)
