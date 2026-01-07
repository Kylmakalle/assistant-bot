from aiogram import Dispatcher

from core import config, misc
from core.load import load_modules
from core.db import db

async def set_db_indexes():
    await db.updates_v2.create_index(
        [("_received_at", 1)],
        name="ttl__received_at__14d",
        expireAfterSeconds=14 * 24 * 60 * 60 # 14 days
    )

async def startup_webhook(dp: Dispatcher):
    await set_db_indexes()
    misc.log.info("Start webhook")
    await dp.bot.set_webhook(config.webhook_url)


async def startup_polling(dp: Dispatcher):
    await set_db_indexes()
    await dp.bot.delete_webhook()


async def shutdown(dp: Dispatcher):
    pass


def main():
    # Include all modules
    load_modules()

    # Register startup/shutdown callbacks
    misc.runner.on_startup(startup_polling, polling=True, webhook=False)
    misc.runner.on_startup(startup_webhook, polling=False, webhook=True)
    misc.runner.on_shutdown(shutdown)
    # Run is selected mode
    if config.use_webhook:
        misc.runner.start_webhook(**config.webhook_server)
    else:
        misc.runner.start_polling(timeout=0)


if __name__ == "__main__":
    main()
