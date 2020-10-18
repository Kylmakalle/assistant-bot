from babel.dates import format_timedelta

from datetime import timedelta


def format_seconds(seconds: int) -> str:
    return format_timedelta(timedelta(seconds=seconds), add_direction=False, locale='ru')
