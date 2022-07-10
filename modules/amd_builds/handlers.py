import logging
import random

from aiogram import types
from aiogram.utils.markdown import hitalic

from core.misc import dp, mp
from modules.amd_builds.consts import StatsEvents
from modules.amd_builds.utils import RedditImageSearcher
from modules.voteban.views import screen_name

INIT_MSGS = (
    "Звоним Лизе Су",
    "Просим Петровича помочь",
    "Спайк разгоняет память",
    "Надо только подождать",
    "Что-же вам на Интуле то не сидится",
    "Ждем заказ из ДНС",
    "Придумайте новые фразы плз",
    "yasobe.ru/na/petrovi4_s_dr ",
    "Еманло выпрямляет ножки",
    '"Только бы не Gigabyte"',
    "Раскрываем потанцевал",
)

error_msgs = (
    "{user}, <b>твою сборку задержали на таможне</b>",
    "{user}, <b>накопленных с обедов денег не хватило на сборку</b>",
    "<b>Ошибка, сори</b>",
    "<b>Автобэкап не выполнен</b>",
    "<b>Все видеокарты раскупили майнеры</b>",
    "<b>Оплата через QIWI не прошла</b>",
)

build_template = '<a href="{link}">&#8203;</a><b>{title}</b>\nu/{user}\n<a href="{reddit_url}">Reddit</a>'

reddit_searcher = RedditImageSearcher()


@dp.message_handler(commands=["amd", "amd_reddit", "amd_build"])
async def cmd_amd_build(m: types.Message, *args, **kwargs):
    return await cmd_reddit_build(m, subreddit="AMD", flair="Battlestation", *args, **kwargs)


@dp.message_handler(commands=["intel", "intel_reddit", "intel_build"])
async def cmd_intel_build(m: types.Message, *args, **kwargs):
    if not m.from_user.is_premium:
        await m.reply(
            "Команда доступна только для Premium ⭐️ пользователей. Приобрети через: @PremiumBot или посмотри свою /amd сборку"
        )
        return
    return await cmd_reddit_build(
        m,
        subreddit="Intel",
        flair="Photo",
        init_msgs=(
            "У вас есть доступ к Premium ⭐ железу, поэтому просто насладитесь моментом",
            "Надеюсь найдётся сборка, а не очередной скриншот из Minecraft",
        ),
        *args,
        **kwargs
    )


async def cmd_reddit_build(m: types.Message, subreddit=None, flair=None, init_msgs=None, *args, **kwargs):
    if not (
        m.chat.username
        in (
            "ru2chhw",
            "Kylmakalle",
        )
        or m.chat.id in (-1001108829366,)
    ):
        await m.reply("Эта команда доступна только в @ru2chhw")
        return

    if not init_msgs:
        init_msgs = INIT_MSGS

    sent = await m.reply(hitalic(random.choice(init_msgs) + "..."), reply=False)

    try:
        build = random.choice(await reddit_searcher.get_images_for_flair(subreddit, flair, limit=200))
    except Exception:
        logging.error("Unable to get build", exc_info=True)
        build = None

    if not build:
        await sent.edit_text(random.choice(error_msgs).format(user=screen_name(m.from_user, True)))

        await mp.track(m.from_user.id, StatsEvents.REDDITBUILD_ERROR, m)
    else:
        await sent.edit_text(
            build_template.format(
                link=build["photo"],
                title=build["title"],
                user=screen_name(m.from_user, True),
                reddit_url=build["reddit_url"],
            )
        )

        await mp.track(m.from_user.id, StatsEvents.REDDITBUILD, m)

    try:
        await m.delete()
    except Exception:
        pass
