from aiogram.utils.callback_data import CallbackData

captcha_cb = CallbackData("captcha", "user_id", "challenge", "answer")


class LogEvents:
    JOINED = "joined"
    CAPTCHA_PASSED = "captcha-passed"
    CAPTCHA_TIMEOUT = "captcha-timeout"
    CAPTCHA_ERROR = "captcha-error"
