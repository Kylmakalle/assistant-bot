from aiogram import types

from core.misc import dp


@dp.message_handler(content_types=types.ContentTypes.ANY, state='*')
async def handle_all_unhandled_messages(message: types.Message):
    """
    Handle all unhanded messages
    """
    print('UNHANDLED MESSAGE', message)
    pass


@dp.callback_query_handler(state='*')
async def handle_all_unhandled_callback_query(query: types.CallbackQuery):
    """
    Handle unregistered callback query data
    """
    print('UNHANDLED QUERY', query)
    pass
