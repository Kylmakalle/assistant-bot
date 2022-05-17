import logging

from core.misc import dp, mp
from aiogram.types import Update

try:
    import ujson as json
except ImportError:
    import json
from core.config import sentry_url
from core.stats import StatsEvents


@dp.errors_handler()
async def all_errors_handler(update: Update, e):
    text = "[DEBUG] Unhandled Error occurred, this is logged"
    if hasattr(update, "message") and (update.message or update.edited_message):
        u = update.message or update.edited_message
        """
        user_id = u.from_user.id
        try:
            await update.bot.send_message(user_id, text=text)
        except Exception:
            pass
        """
    elif hasattr(update, "callback_query") and update.callback_query:
        u = update.callback_query
        try:
            await update.bot.answer_calback_query(update.callback_query.id, text=text)
        except Exception:
            pass
    else:
        u = None
    logging.exception(f"The update was: {json.dumps(update.to_python(), indent=4)}", exc_info=True)

    if not sentry_url:
        await mp.track(0, StatsEvents.ERROR, u)
    return True
