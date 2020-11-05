from babel.dates import format_timedelta
from durations import Duration
from durations.helpers import valid_duration
from durations.exceptions import InvalidTokenError
from datetime import timedelta, datetime, date
import pytz


def format_seconds(seconds: int) -> str:
    return format_timedelta(timedelta(seconds=seconds), add_direction=False, locale='ru')


def get_time_args(args: str):
    args_list = args.split(' ')
    invalid_tokens = []
    while True:
        try:
            time_string = ''.join(args_list)
            is_valid_duration = valid_duration(time_string)
            if is_valid_duration and time_string.isascii():
                break
            else:
                raise InvalidTokenError
        except InvalidTokenError:
            if args_list:
                invalid_tokens.append(args_list[-1])
                del args_list[-1]
            else:
                break
    return args_list, list(reversed(invalid_tokens))


def get_restrict_text(chat: dict, restrict_type: str, till_next_day: bool = False) -> str:
    if till_next_day:
        text = "Пользователь ограничен <b>до конца дня</b>."
    else:
        text = "Пользователь ограничен на {human_time}."
    if restrict_type == "ban":
        if till_next_day:
            text = "Пользователь в муте <b>до конца дня</b>."
        else:
            text = "Пользователь в муте на {human_time}."

        if chat.get('username') == 'ru2chhw':
            if till_next_day:
                text = "Пользователь пошёл разгонять память <b>до конца дня</b>. Ждём с результатом!"
            else:
                text = "Пользователь пошёл разгонять память {human_time}. Ждём с результатом!"
        elif chat.get('username') == 'velach':
            if till_next_day:
                text = "Пользователь пошёл парафинить цепь <b>до конца дня</b>. Ждём с результатом!"
            else:
                text = "Пользователь пошёл парафинить цепь {human_time}. Ждём с результатом!"
        elif chat.get('username') == 'ru2chmobi':
            if till_next_day:
                text = "Пользователь пошёл прошивать кастом <b>до конца дня</b>. Ждём с кирпичом!"
            else:
                text = "Пользователь пошёл прошивать кастом {human_time}. Ждём с кирпичом!"

    elif restrict_type == "unmedia":
        if till_next_day:
            text = "Пользователь без медии <b>до конца дня</b>."
        else:
            text = "Пользователь без медии на {human_time}."

    return text


def get_next_day_msk() -> datetime:
    today = datetime.now(pytz.timezone('Europe/Moscow'))
    tomorrow = today + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
