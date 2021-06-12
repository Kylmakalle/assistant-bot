import asyncio
import logging
import random
from random import uniform

import aiohttp
from aiogram.utils.json import json
from aiogram.utils.markdown import hitalic

from modules.amd_builds.consts import REDDIT_URL, USER_AGENT

log = logging.getLogger('amd_builds')


def load_videocards():
    with open('data/videocards.json') as file:
        return json.load(file)


def load_cpus():
    with open('data/cpu.json') as file:
        return json.load(file)


def get_build_title(name):
    return f'{name}: f{hitalic("My new AMD <3 build")}'


async def request_builds(amount):
    res = []
    after = None

    errors = 0

    async with aiohttp.ClientSession() as session:
        while True:
            params = {'allow_over18': '1', 'q': 'flair_name%3A%22Battlestation%22', 't': 'all',
                      'restrict_sr': '1'}
            if after:
                params['after'] = after
            headers = {'User-Agent': USER_AGENT}
            try:

                async with session.get(REDDIT_URL, params=params, headers=headers) as resp:
                    log.info(f'REDDIT RESPONSE {await resp.text()}')
                    r = await resp.json()
                    posts = r.get('posts')
                    if posts:
                        for key in posts:
                            res.append(posts[key])
                        after = r['postOrder'][-1]
                    else:
                        log.exception(f'No posts in reddit api, {posts}')
                        raise ValueError
            except (aiohttp.ClientError, ValueError, IndexError, KeyError) as e:
                log.exception('Reddit Error', exc_info=True)
                errors += 1
            if errors > 10:
                break
            if len(res) >= amount:
                break
            sleep_time = uniform(0.2, 1.5)
            log.info(f'Reddit Sleeping {sleep_time}')
            await asyncio.sleep(sleep_time)
    return res


async def get_build(amount=100):
    builds = await request_builds(amount)
    log.info(
        f'BUILDS AMOUNT {len(builds)}'
    )
    if builds:
        photo = None
        random.shuffle(builds)
        while True:
            random_build = random.choice(builds)
            log.info(f'RANDOMBUILD {random_build["id"]}')
            photo = get_build_photo(random_build)
            if photo:
                log.info(f'SENT Random build {random_build["id"]}')
                return {'photo': photo, 'title': random_build['title'], 'reddit_url': random_build['permalink']}
    else:
        return


def get_build_photo(build):
    log.info(f"Reddit JSON post {json.dumps(build)}")
    try:
        if build['media']['type'] == 'gallery':
            for photo_id in build['media']['gallery']['items']:
                if build['media']['mediaMetadata'][photo_id]['e'] == 'Image':
                    return build['media']['mediaMetadata'][photo_id]['s']['u']
        elif build['media']['type'] != 'embed':
            if 'content' in build['media']:
                return build['media']['content']

    except Exception as e:
        log.error(f'Error media-content {e}')
        pass

    try:
        return build['source']['url']
    except Exception as e:
        log.error(f'Error source-url {e}')
        pass
