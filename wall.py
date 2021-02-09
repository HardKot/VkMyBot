import sqlite3
import vk_api
from vk_api.utils import get_random_id

from options import Walls
from options import __TOKEN__, __DB__, __POSTFILTERS__

vk_session = vk_api.VkApi(token=__TOKEN__)

{'id': 5, 'from_id': -202399435, 'owner_id': -202399435, 'date': 1612777097, 'marked_as_ads': 0, 'post_type': 'post', 'text': 'Новости Тетс', 'can_edit': 1,
    'created_by': 330315179, 'can_delete': 1, 'comments': {'count': 0}, 'is_favorite': False, 'donut': {'is_donut': False}, 'short_text_rate': 0.8}

def run(info):
    wall = Walls(info['id'])
    wall.handling(info['content'])
    subscibers = []
    with sqlite3.connect(__DB__) as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM `users`')
        result = cursor.fetchall()
        for user in result:
            subscibers.append({'id': user[0], 'filter':user[4]})
    for subsciber in subscibers:
        if wall.title:
            if wall.title in subsciber['filter']:
                info = wall.message()
                info['user_id'] = subsciber['id']
                info['random_id'] = get_random_id()
                vk_session.method('messages.send', info)
