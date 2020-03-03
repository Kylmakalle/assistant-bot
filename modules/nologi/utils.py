# А нафига нам в БД хранить то всё? Можно в рантайме

import aiohttp
import aiohttp.client_exceptions
from datetime import datetime, timedelta

RATES_URL = "https://www.sberbank.ru/portalserver/proxy/"
RATES_PARAMS = {'pipe': "shortCachePipe",
                'url': 'http://localhost/rates-web/rateService/rate/current?regionId=77&rateCategory=base&currencyCode=978&currencyCode=840'}
RATES_HEADERS = {
    'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}

RATES_UPDATE = None
RATES = {}


async def get_rates():
    global RATES_UPDATE
    if 'EUR' in RATES and 'USD' in RATES:
        if RATES_UPDATE:
            if RATES_UPDATE + timedelta(hours=8) <= datetime.utcnow():
                return RATES

    fetched_rates = await fetch_rates()
    try:
        usd_price = fetched_rates['base']['840']['0']['sellValue']
    except KeyError:
        usd_price = 67.03
    try:
        eur_price = fetched_rates['base']['978']['0']['sellValue']
    except KeyError:
        eur_price = 72.93

    RATES_UPDATE = datetime.utcnow()
    RATES['EUR'] = eur_price
    RATES['USD'] = usd_price

    return RATES


async def fetch_rates():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(RATES_URL, params=RATES_PARAMS, headers=RATES_HEADERS) as resp:
                r = await resp.json()
                return r
    except (aiohttp.client_exceptions.ClientError, ValueError) as e:
        print(e)
        return {}


def ffloat(value):
    return ("%.2f" % value).rstrip('0').rstrip('.')


def format_fiat(symbol, value):
    pos = [value, symbol]
    if symbol == 'USD':
        pos[0] = '$'
        pos[1] = value
    elif symbol == 'RUB':
        pos[0] = value
        pos[1] = 'руб.'
    elif symbol == 'EUR':
        pos[0] = value
        pos[1] = '€'
    else:
        pass
    return '{} {}'.format(pos[0], pos[1])
