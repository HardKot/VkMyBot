

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from options import Users
from options import POSTFILTERS, conn, logging
from options import __TOKEN__, __DB__, __ADMINGROUP__, __POSTFILTERS__


vk_session = vk_api.VkApi(token=__TOKEN__)

def commands(command, user):
    if not user.checkWork():
        if command in ['Начать']:
            vk_session.method('messages.send', {'user_id': user.id,
                                        'random_id': get_random_id(),
                                        'message': 'Йоп! Коротко пробежимся, на данный момент есть только ф-ция рассылки она оповестит тебя о чем-то. \n Красынй цвет - полность отключен \n Зеленный - полность включена.',
                                        'keyboard': user.createKeyboard().get_keyboard()})
        elif command in ['Рассылка']:
            user.reSpam()
            vk_session.method('messages.send', {'user_id': user.id,
                                        'random_id': get_random_id(),
                                        'message': 'Твой уровень расслыки изменен.',
                                        'keyboard': user.createKeyboard().get_keyboard()})
        elif command in ['Фильтры']:
            user.work('filter')
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
            if len(user.postFilter) == 0:
                filterlist = 'У тебя нет подписок.'
            else:
                filterlist = 'Ты подписан на '
                for post in user.postFilter:
                    filterlist += post + ', '
                else:
                    filterlist = filterlist[:-2] + '.'
            vk_session.method('messages.send', {'user_id': user.id,
                                                'random_id': get_random_id(),
                                                'message':  filterlist + '\n Введи новые номера фильтров(слитно) или отмена.\n' + POSTFILTERS(),
                                                'keyboard': keyboard.get_keyboard()})
            
    else:
        if user.checkWork() == 'filter':
            if not command in ['Отмена', 'отмена']:
                user.reFilter(command)
                vk_session.method('messages.send', {'user_id': user.id,
                                                    'random_id': get_random_id(),
                                                    'message': 'Список получаемых тобой постов изменен.',
                                                    'keyboard': user.createKeyboard().get_keyboard()})
            else:
                vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                ), 'message': 'Ты будешь получать все те же посты...', 'keyboard': user.createKeyboard().get_keyboard()})
            user.work(None)



def commands_plus(command, user):
    if not user.checkWork():
        if command in ['Массовая отправка', 'Spam']:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
            vk_session.method('messages.send', {'user_id': user.id,
                                        'random_id': get_random_id(),
                                        'message': 'Отправь мне сообщение, а я разошлю всем.\n Напиши отмена или нажми кнопку ниже',
                                        'keyboard': keyboard.get_keyboard()})
            user.work('Spam')
        elif command in ['Изменить роль', 'роли'] and user.status == 'admin':
            listname = ''
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
            vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(), 'message': 'Список \n' + user.createdSubscribe(vk_session) + 'Доступные роли: user, head, admin, test \n"Роль номер',
                                                'keyboard': keyboard.get_keyboard()})
            user.work('reRole')
    else:
        if user.lastCommand == 'Spam':
            if not command in ['Отмена', 'отмена']:
                users = user.getOtherUser(' and "mailing"=1')
                for user_id in users:
                    vk_session.method('messages.send', {'user_id': user_id, 'random_id': get_random_id(), 'message': command})
                vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                    ), 'message': 'Сообщения успешно всем отправлены', 'keyboard': user.createKeyboard().get_keyboard()})
            else:
                vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(), 'message': 'Ожидаю другие приказы!', 'keyboard': user.createKeyboard().get_keyboard()})
            user.work(None)
        elif user.lastCommand == 'reRole':
            if not command in ['Отмена', 'отмена']:
                if not command:
                    return
                if command[4] == ' ':
                    role = command[:4]
                    number = command[5:]
                else: 
                    number = command[6:]
                    role = command[:5]
                sql = 'SELECT * FROM "subscriber" WHERE "number"={}'.format(number)
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    user_id = cursor.fetchone()
                    conn.commit()
                    Users(user_id[0]).reStarus(role)
                    name = vk_session.method(
                        'users.get', {'user_ids': user_id[0], 'name_case': 'Nom'})[0]
                    vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                    ), 'message': '{0} {1} успешно получил {2}'.format(name['first_name'], name['last_name'], role), 'keyboard': user.createKeyboard().get_keyboard()})
            else:
                vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                ), 'message': 'Жду другие команды!', 'keyboard': user.createKeyboard().get_keyboard()})
            user.work(None)

def run(info):
    user = Users(info['id'])
    #print(info['content']['message'], user.id)
    commands(command=info['content']['message'], user=user)
    if user.status in __ADMINGROUP__:
        commands_plus(command=info['content']['message'], user=user)
