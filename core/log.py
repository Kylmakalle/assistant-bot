from aiogram.utils.markdown import hbold, hlink

from core.config import log_channel
from core.misc import bot
from modules.voteban.views import screen_name
import logging


def form_log(chat: dict, user: dict, event: str, message_id: int = None, admin: dict = None, **kwargs):
    text = f'#{event.upper().replace("-", "_")}\n'
    if admin:
        text += f"• {hbold('Admin:')} {screen_name(admin, tag=False)} [#id{admin['id']}]" + '\n'
    if chat:
        text += f"• {hbold('Chat:')} {chat['title']} [#chat{abs(chat['id'])}]" + '\n'
    text += f"• {hbold('User:')} {screen_name(user)} [#id{user['id']}]" + '\n'
    if kwargs:
        for kwarg in kwargs:
            text += f"• {hbold(kwarg.capitalize().replace('_', ' ') + ':')} {kwargs[kwarg]}" + '\n'
    if message_id and chat.get('username'):
        text += f"• {hlink('Перейти к сообщению', 'https://t.me/{}/{}'.format(chat['username'], message_id))}" + '\n'

    return text


async def send_log(*args, **kwargs):
    try:
        await bot.send_message(*args, **kwargs)
    except:
        logging.exception(f'ERROR SENDING LOG: {args}, {kwargs}', exc_info=True)


async def log(text='Logged event', event='event', chat: dict = None, user: dict = None, admin: dict = None,
              message_id: int = None,
              log_ch: [list, int, str] = None, text_kwargs: dict = None, log_kwargs: dict = None):
    if not log_kwargs:
        log_kwargs = {}
    if not 'disable_web_page_preview' in log_kwargs:
        log_kwargs.update(dict(disable_web_page_preview=True))
    if not text_kwargs:
        text_kwargs = {}
    if chat and user:
        text = form_log(chat, user, event, message_id, admin, **text_kwargs)
    if log_channel:
        await send_log(chat_id=log_channel, text=text, **log_kwargs)
    if chat.get('log_ch'):
        await send_log(chat_id=chat['log_ch'], text=text, **log_kwargs)
    if log_ch:
        if isinstance(log_ch, int) or isinstance(log_ch, str):
            await send_log(chat_id=log_ch, text=text, **log_kwargs)
        elif isinstance(log_ch, list):
            for chid in log_ch:
                await send_log(chat_id=chid, text=text, **log_kwargs)
