import vk_api
from vk_api.utils import get_random_id

from options import Walls, conn
from options import __TOKEN__, __DB__, __POSTFILTERS__

vk_session = vk_api.VkApi(token=__TOKEN__)

def run(info):
    wall = Walls(info['id'])
    wall.handling(info['content'])
    subscibers = []
    with conn.cursor as cursor:
        cursor.execute('SELECT * FROM "users"')
        result = cursor.fetchall()
        conn.commit()
        for user in result:
            subscibers.append({'id': user[0], 'filter':user[4]})
    for subsciber in subscibers:
        if wall.title:
            if wall.title in subsciber['filter']:
                info = wall.message()
                info['user_id'] = subsciber['id']
                info['random_id'] = get_random_id()
                vk_session.method('messages.send', info)
