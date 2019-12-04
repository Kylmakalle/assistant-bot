import random
import string
import xml.etree.cElementTree

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hitalic

from core.db import db
from modules.captcha_button.consts import captcha_cb
from modules.voteban.views import screen_name

EMOJI_DATA = []

# Preload emojis
root = xml.etree.ElementTree.parse('modules/captcha_button/annotations/ru.xml').getroot()
annotations = root[1]
for child in annotations:
    if not child.attrib.get('type', '') == 'tts':
        continue
    EMOJI_DATA.append({'emoji': child.attrib['cp'], 'description': child.text})

MAX_EMOJIS = 5


def genkey():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


async def get_welcome_message(user, title, join_msg_id):
    emojis = random.sample(EMOJI_DATA, MAX_EMOJIS)
    for emoji in emojis:
        emoji['hash'] = genkey()
    answer = random.sample(emojis, 1)[0]
    sample_welcome_message = 'Привет, {}! Добро пожаловать в <b>{}</b>.\n'.format(screen_name(user), title)
    sample_welcome_message += 'Выбери эмодзи: ' + hitalic(
        answer['description'].capitalize())
    kb = InlineKeyboardMarkup(row_width=MAX_EMOJIS)
    ch = {'user_id': user['id'], 'answer': answer['hash'], 'join_msg_id': join_msg_id}
    challenge = await db.c_challenges.insert_one(ch)

    kb.add(*[InlineKeyboardButton(emoji['emoji'], callback_data=
    captcha_cb.new(user_id=str(user['id']),
                   challenge=str(challenge.inserted_id),
                   answer=emoji['hash'])) for emoji in emojis])
    return sample_welcome_message, kb


async def get_user_msgs_to_delete_date(chat_id, user_id, date, ignore_id=None):
    q = {'message.chat.id': chat_id, 'message.from.id': user_id, 'message.date': {'$gte': date}}
    if ignore_id:
        q.update({'message.message_id': {'$ne': ignore_id}})
    updates = await db.updates.find(q).to_list(None)
    return updates
