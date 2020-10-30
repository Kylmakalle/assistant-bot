from babel.dates import format_timedelta
from durations import Duration
from durations.helpers import valid_duration
from durations.exceptions import InvalidTokenError
from datetime import timedelta


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


def get_restrict_text(chat: dict, restrict_type: str) -> str:
    text = "Пользователь ограничен на {human_time}."
    if restrict_type == "ban":
        text = "Пользователь в муте на {human_time}."

        if chat.get('username') == 'ru2chhw':
            text = "Пользователь пошёл разгонять память {human_time}. Ждём с результатом!"
        elif chat.get('username') == 'velach':
            text = "Пользователь пошёл парафинить цепь {human_time}. Ждём с результатом!"
        elif chat.get('username') == 'ru2chmobi':
            text = "Пользователь пошёл прошивать кастом {human_time}. Ждём с кирпичом!"

    elif restrict_type == "unmedia":
        text = "Пользователь без медии на {human_time}."

        # if chat.get('username') == 'ru2chhw':
        #     text = "Пользователь пошёл разгонять память {human_time}. Ждём с результатом!"
        # elif chat.get('username') == 'velach':
        #     text = "Пользователь пошёл парафинить цепь {human_time}. Ждём с результатом!"
        # elif chat.get('username') == 'ru2chmobi':
        #     text = "Пользователь пошёл прошивать кастом {human_time}. Ждём с кирпичом!"

    return text
