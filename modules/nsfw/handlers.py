from aiogram import types

from core.config import git_repository
from core.misc import dp, mp
from core.stats import StatsEvents


@dp.message_handler(commands=['nsfw', 'sfw'], state='*')
async def cmd_nsfw(message: types.Message):
    """
    Handle all unhanded messages
    """
    await message.reply(f"Feature not implemented yet, stay tuned! {git_repository}")
    await mp.track(message.from_user.id, StatsEvents.NSFW, message)
