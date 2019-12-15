from aiogram.utils.callback_data import CallbackData
import random

voter = CallbackData('voter', 'chat_id', 'user_id')

from modules.captcha_button.consts import LogEvents


class LogEvents(LogEvents):
    VOTEBAN = 'voteban'
    BAN = 'BAN'
    KICK = 'KICK'


ADMIN_REPORT_RESPONSES = [
    'Маленький шаг в сторону бана, анимешник.',
    'Так-так, что тут у нас? Образованный, революционер...',
    'Telegram не любит амдшников.',
    'План по репортам за день выполнен, пора банить.',
    'Пойди это Петровичу расскажи.',
    'Вот ты и попался, анимешник!'
]


def get_admin_report_response():
    return random.sample(ADMIN_REPORT_RESPONSES, 1)[0]
