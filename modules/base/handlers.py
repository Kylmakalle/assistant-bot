import logging
import traceback

from core.misc import dp, mp
from core.stats import StatsEvents


@dp.errors_handler()
async def all_errors_handler(update, e):
    text = '[DEBUG] Unhandled Error occurred, this is logged'
    if hasattr(update, 'message') and (update.message or update.edited_message):
        u = update.message or update.edited_message
        user_id = u.from_user.id
        """
        try:
            await update.bot.send_message(user_id, text=text)
        except:
            pass
        """
    elif hasattr(update, 'callback_query') and update.callback_query:
        user_id = update.callback_query.from_user.id
        u = update.callback_query
        try:
            await update.bot.answer_calback_query(update.callback_query.id, text=text)
        except:
            pass
    else:
        u = None
    logging.error(f'The update was: {update}')
    logging.exception(traceback.print_exc())
    await mp.track(0, StatsEvents.ERROR, u)
    return True
