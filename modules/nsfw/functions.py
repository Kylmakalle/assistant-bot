from clarifai.rest import ClarifaiApp
from core.config import clarifai_token
from core.db import db
from statistics import mean

app = ClarifaiApp(api_key=clarifai_token)
model = app.public_models.nsfw_model


async def check_nsfw(url, file_id=None, is_video=False):
    saved_prediction = await db.nsfw.find_one({'_id': file_id})
    if saved_prediction:
        nsfw = saved_prediction['nsfw']
        sfw = saved_prediction['sfw']
    else:
        response = model.predict_by_url(url, is_video=is_video)
        sfw = 100
        nsfw = 0

        if response['outputs'][0]['data'].get('frames'):
            sfw_list = []
            nsfw_list = []
            for frame in response['outputs'][0]['data']['frames']:
                for concept in frame['data']['concepts']:
                    if concept['name'] == 'sfw':
                        sfw_list.append(concept['value'])
                    else:
                        nsfw_list.append(concept['value'])
            sfw = mean(sfw_list)
            nsfw = mean(nsfw_list)
        else:
            for concept in response['outputs'][0]['data']['concepts']:
                if concept['name'] == 'sfw':
                    sfw = concept['value']
                else:
                    nsfw = concept['value']

        await db.nsfw.insert_one({'_id': file_id, 'nsfw': nsfw, 'sfw': sfw})
    return {'nsfw': nsfw, 'sfw': sfw}
