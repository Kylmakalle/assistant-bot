from aiogram.utils.markdown import hitalic
from aiogram.utils.json import json
from modules.amd_builds.consts import REDDIT_URL, USER_AGENT
import aiohttp
from random import uniform
import random
import asyncio


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
                    r = await resp.json()
                    posts = r['posts']
                    if posts:
                        for key in posts:
                            res.append(posts[key])
                        after = r['postOrder'][-1]
                    else:
                        raise ValueError
            except (aiohttp.ClientError, ValueError, IndexError, KeyError) as e:
                print('Reddit Error', e)
                errors += 1
            if errors > 10:
                break
            if len(res) >= amount:
                break
            sleep_time = uniform(0.2, 1.5)
            print('Reddit Sleeping', sleep_time)
            await asyncio.sleep(sleep_time)
    return res


async def get_build(amount=100):
    builds = await request_builds(amount)
    print(
        'BUILDS AMOUNT', len(builds)
    )
    if builds:
        photo = None
        while True:
            random_build = random.choice(builds)
            print('RANDOMBUILD', random_build['id'])
            photo = get_build_photo(random_build)
            if photo:
                print(random_build['id'], 'SENT')
                return {'photo': photo, 'title': random_build['title']}
    else:
        return


def get_build_photo(build):
    reddit_source = None
    try:
        reddit_source = build['media']['content']
    except:
        pass
    if reddit_source:
        try:
            return build['media']['content']
        except:
            pass
    else:
        try:
            return build['source']['url']
        except Exception as e:
            print('error ex source', e)
            pass
