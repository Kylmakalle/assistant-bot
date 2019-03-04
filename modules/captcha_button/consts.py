from aiogram.utils.callback_data import CallbackData

captcha_cb = CallbackData('captcha', 'user_id', 'var')


class LogEvents:
    JOINED = 'joined'
    CAPTCHA_PASSED = 'captcha-passed'
    CAPTCHA_TIMEOUT = 'captcha-timeout'
