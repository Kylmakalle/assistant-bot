from typing import Optional, Union, List

from aiogram.utils.json import json
from aiogram.bot import Bot
from aiogram.utils.payload import generate_payload

# fmt: off
AVAILABLE_MESSAGE_REACTIONS = ["👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]
# fmt: on


def convert_reaction_type(reactions: List[str]) -> List[dict]:
    return [{"type": "emoji", "emoji": reaction} for reaction in reactions]


async def set_message_reaction(
    bot: Bot,
    chat_id: Union[str, int],
    message_id: int,
    reaction: List[str] = None,
    is_big: Optional[bool] = None,
) -> bool:
    if reaction is not None:
        reaction = json.dumps(convert_reaction_type(reaction))
    payload = generate_payload(exclude=["bot"], **locals())
    return await bot.request("setMessageReaction", payload)
