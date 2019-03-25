import json
import base64
import datetime
import time

import aiohttp
import aiohttp.client_exceptions
from aiogram.types import CallbackQuery, Message

TRACK_URL = 'http://api.mixpanel.com/track'


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            fmt = '%Y-%m-%dT%H:%M:%S'
            return obj.strftime(fmt)

        return json.JSONEncoder.default(self, obj)


class Mixpanel:
    def __init__(self, token, serializer=DatetimeSerializer):
        self._token = token
        self._serializer = serializer

    def json_dumps(self, data, cls=None):
        # Separators are specified to eliminate whitespace.
        return json.dumps(data, separators=(',', ':'), cls=cls)

    async def track(self, user_id, event_name, aiogram_obj=None, properties=None, meta=None):
        if not self._token:
            return False
        all_properties = {
            'token': self._token,
            'distinct_id': user_id,
            'time': int(time.time()),
            # 'mp_lib': 'python',
            # '$lib_version': '0.1',
        }
        if aiogram_obj:
            if isinstance(aiogram_obj, Message):
                p = {}
                if aiogram_obj.chat.type == 'private':
                    p['chat_type'] = 'private'
                else:
                    p['chat_id'] = aiogram_obj.chat.id
                    p['chat_type'] = aiogram_obj.chat.type
                    p['chat_title'] = aiogram_obj.chat.title
                if aiogram_obj.text:
                    p['text'] = aiogram_obj.text
                if aiogram_obj.caption:
                    p['caption'] = aiogram_obj.caption
                p['message_type'] = aiogram_obj.content_type
                all_properties.update(p)
            elif isinstance(aiogram_obj, CallbackQuery):
                p = {}
                if aiogram_obj.message.chat.type == 'private':
                    p['chat_type'] = 'private'
                else:
                    p['chat_id'] = aiogram_obj.message.chat.id
                    p['chat_type'] = aiogram_obj.message.chat.type
                    p['chat_title'] = aiogram_obj.message.chat.title
                all_properties.update(p)
            else:
                all_properties.update(aiogram_obj.to_python())
        if properties:
            all_properties.update(properties)
        event = {
            'event': event_name,
            'properties': all_properties,
        }
        if meta:
            event.update(meta)

        json_message = self.json_dumps(event, cls=self._serializer)
        params = {
            'data': base64.b64encode(json_message.encode('utf8')).decode("utf-8"),
            'verbose': 1,
            'ip': 0,
        }

        headers = {'Content-type': 'application/json'}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(TRACK_URL, params=params, headers=headers) as resp:
                    r = await resp.json()
                    if r['status'] != 1:
                        raise ValueError('Error in Mixpanel request: ' + r.get('error', 'None'))
                    return r
        except (aiohttp.client_exceptions.ClientError, ValueError) as e:
            print(e)
            return False
