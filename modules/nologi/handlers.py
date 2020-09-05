from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from aiogram.utils.markdown import hlink, hbold, hcode, hitalic

from core.misc import dp, mp, bot

from modules.nologi.utils import get_rates, ffloat, format_fiat


@dp.message_handler(
    commands=['nolog', 'nologi', 'nalog', 'nalogi', 'налог', 'нологи', 'нолохи', 'нолох', 'noloh', 'nolox', 'ploti',
              'plati'],
    commands_prefix='!/')
async def cmd_nolog(m: types.Message, user: dict, chat: dict):
    text = "Рассчёт таможенных пошлин для РФ" + '\n\n'

    cmd = hcode("/nolog <цена товара в EUR>") + '\n'
    cmd += hcode("/nolog <цена товара> <валюта>") + '\n'

    example_cmd = "Пример:" + " " + "/nolog 465.98" + '\n\n'

    available_curs = "Доступные валюты: <b>EUR, USD, RUB/RUR</b>"
    about = "\n" + hitalic(
        "По курсу Сбербанка. Цена товара должна быть без учёта доставки. Посылки тяжелее 31кг считаются отдельно!") + " " + \
            hlink("Подробнее", "https://qwintry.com/ru/duty-calc")

    text = text + cmd + example_cmd + available_curs + about

    if len(m.text.split()) > 1:
        while True:
            rates = await get_rates()
            args = m.text.split()
            price = args[1]
            currency = 'EUR'
            if len(args) > 2:
                currency = args[2]

            try:
                nice_price = float(price)
            except:
                break

            if currency.upper() not in ('USD', 'EUR', 'RUB', 'RUB'):
                break

            currency = currency.upper()

            threshold = 200
            if currency == 'USD':
                threshold = rates['EUR'] / rates['USD'] * threshold

            if currency in ('RUB', 'RUR',):
                threshold = rates['EUR'] * threshold

            if nice_price <= threshold:
                text = "✅ <b>Плотить не надо!</b>\nЦена меньше порога в {}".format(
                    format_fiat(currency, ffloat(threshold)))
                break
            else:
                fix_fee = 4  # fix
                fee = (nice_price - threshold) * 0.15  # 15% above price
                total_fee = fee + fix_fee

                total_overpay = (abs(nice_price + total_fee - nice_price) / nice_price) * 100.0

                # TODO: Disable rub for rub
                other_curr = 'RUB'  # if currency not in ('RUB', 'RUR') else 'USD'

                text = f"🤑 {hbold('Плоти нолохи.')}"

                text += f"\nТаможенная пошлина с покупки на {format_fiat(currency, ffloat(nice_price))} ({format_fiat(other_curr, ffloat(nice_price * rates[other_curr]))}) " \
                        f"составит: {format_fiat(currency, ffloat(total_fee))} " \
                        f"({format_fiat(other_curr, ffloat(total_fee * rates[other_curr]))})"  # \n" \
                text += f"\n\nИтоговая стоимость: {hbold(format_fiat(currency, ffloat(nice_price + total_fee)))} ({format_fiat(other_curr, ffloat((nice_price + total_fee) * rates[other_curr]))})"

                text += f"\nИтоговая переплата: {ffloat(total_overpay)}%"
                if total_overpay > 20:
                    text += ". " + hbold("Это больше чем НДС!")

                # text += "\n\nФормула: " + hitalic(
                #    f'Фикс. пошлина {format_fiat(currency, fix_fee)} + 15% от суммы превышения ({ffloat(nice_price)} - {ffloat(threshold)}) * 15% = {format_fiat(currency, ffloat(fee))})')
                text += "\nБыстро сравнить цены можно на " + "hardprice.ru" + "\n" + \
                        hlink("Подробнее о пошлине", "https://qwintry.com/ru/duty-calc")
            break

    reply_to_message = None
    if m.reply_to_message:
        reply_to_message = m.reply_to_message.message_id

    await bot.send_message(m.chat.id, text, reply_to_message_id=reply_to_message, disable_web_page_preview=True)

    try:
        await bot.delete_message(m.chat.id, m.message_id)
    except:
        pass
