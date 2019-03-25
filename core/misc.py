import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils.executor import Executor
import sentry_sdk

from core import config
from core.packages import PackagesLoader
from mixpanel import Mixpanel

logging.basicConfig(level=logging.INFO)

log = logging.getLogger('assistant')

loop = asyncio.get_event_loop()

bot = Bot(config.bot_token, parse_mode=ParseMode.HTML, validate_token=False)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)
runner = Executor(dp, skip_updates=config.skip_updates)

loader = PackagesLoader()

dp.middleware.setup(LoggingMiddleware('bot'))

mp = Mixpanel(config.mixpanel_key)

if config.sentry_url:
    sentry_sdk.init(config.sentry_url)
