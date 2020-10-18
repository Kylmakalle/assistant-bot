from babel.dates import format_timedelta
from durations import Duration
from durations.exceptions import InvalidTokenError
from datetime import timedelta


def format_seconds(seconds: int) -> str:
    return format_timedelta(timedelta(seconds=seconds), add_direction=False, locale='ru')


def get_time_args(args: str):
    args_list = args.split(' ')
    invalid_tokens = []
    while True:
        try:
            Duration(' '.join(args_list))
            break
        except InvalidTokenError:
            invalid_tokens.append(args_list[-1])
            del args_list[-1]

    return args_list, invalid_tokens
