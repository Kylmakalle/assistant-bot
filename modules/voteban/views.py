from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hlink

from modules.voteban.consts import voter


def render_voteban_kb(voteban: dict) -> InlineKeyboardMarkup:
    votes_count = len(voteban.get("votes", []))

    if votes_count:
        votes_str = f" ({votes_count})"
    else:
        votes_str = ""

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "Бан!" + votes_str,
            callback_data=voter.new(chat_id=str(voteban["chat_id"]), user_id=str(voteban["user_id"])),
        )
    )

    return kb


def screen_name(user: [dict, types.User], tag=True) -> str:
    if isinstance(user, types.User):
        user = user.to_python()
    title = user["first_name"] + (f" {user['last_name']}" if user.get("last_name") else "")
    if tag:
        return hlink(title, f"tg://user?id={user['id']}")
    else:
        return title
