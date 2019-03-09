from aiogram.utils.callback_data import CallbackData

voter = CallbackData('voter', 'chat_id', 'user_id')

from modules.captcha_button.consts import LogEvents


class LogEvents(LogEvents):
    VOTEBAN = 'voteban'
