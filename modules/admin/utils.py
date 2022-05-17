from datetime import timedelta, datetime

import pytz
from aiogram import types
from babel.dates import format_timedelta
from durations.exceptions import InvalidTokenError
from durations.helpers import valid_duration

from core import db


def format_seconds(seconds: int) -> str:
    return format_timedelta(timedelta(seconds=seconds), add_direction=False, locale="ru")


def get_time_args(args: str):
    args_list = args.split(" ")
    invalid_tokens = []
    while True:
        try:
            time_string = "".join(args_list)
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

        if chat.get("username") == "ru2chhw":
            if till_next_day:
                text = "Пользователь пошёл разгонять память <b>до конца дня</b>. Ждём с результатом!"
            else:
                text = "Пользователь пошёл разгонять память {human_time}. Ждём с результатом!"
        elif chat.get("username") == "velach":
            if till_next_day:
                text = "Пользователь пошёл парафинить цепь <b>до конца дня</b>. Ждём с результатом!"
            else:
                text = "Пользователь пошёл парафинить цепь {human_time}. Ждём с результатом!"
        elif chat.get("username") == "ru2chmobi":
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
    today = datetime.now(pytz.timezone("Europe/Moscow"))
    tomorrow = today + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)


def get_substring_line(string, substring) -> int:
    for line, item in enumerate(string.split("\n")):
        if substring in item:
            return line

    return -1


async def get_user_id(m: types.Message):
    uid = None
    for entity in m.entities or m.caption_entities:
        if entity.type == types.MessageEntityType.MENTION:  # noqa: E721
            mention = entity.get_text(m.text)
            if get_substring_line(m.text, mention) != 0:
                continue
            user = await db.users.find_one({"username": {"$regex": mention.replace("@", ""), "$options": "i"}})
            if not user:
                continue
            else:
                uid = user["id"]
                break
        elif entity.type == types.MessageEntityType.HASHTAG:  # noqa: E721
            hashtag = entity.get_text(m.text)
            if get_substring_line(m.text, hashtag) != 0:
                continue
            if hashtag.startswith("#id") and len(hashtag) > 3:
                uid = int(hashtag.replace("#id", ""))
                break
        elif entity.type == types.MessageEntityType.TEXT_MENTION:  # noqa: E721
            if get_substring_line(m.text, entity.get_text(m.text)) != 0:
                continue
            uid = entity.user.id
            break
    if not uid:
        args = m.text.split()
        if not args:
            m.text = " ".join(m.text.split())
            cmd, args = m.text.split(" ", 1)
        else:
            if len(args) > 1:
                args = args[1]
            else:
                raise Exception("No uid found")
        try:
            uid = int(args.strip())
        except Exception:
            pass
    if not uid:
        raise Exception("No uid found")
    else:
        return uid


def can_user_ban(user: types.ChatMember, db_user: dict) -> bool:
    return (
        isinstance(user, (types.ChatMemberMember, types.ChatMemberOwner))
        and user.can_restrict_members
        or user.status == "creator"
        or db_user.get("status", 0) >= 3
    )
