import datetime
import sqlite3

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from options import Users
from options import POSTFILTERS
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
            with sqlite3.connect(__DB__) as db:
                cursor = db.cursor()
                cursor.execute('SELECT `id` FROM `users` WHERE NOT `id`=?',(user.id,))
                result = cursor.fetchall()
                cursor.execute('DELETE FROM `subscriber`')
                db.commit()
                i = 1
                for subscriber in result:
                    info = vk_session.method('users.get', {'user_ids' : subscriber[0], 'name_case':'Nom'})[0]
                    cursor.execute('INSERT INTO `subscriber` VALUES (?,?)',
                                   (subscriber[0],i))
                    db.commit()
                    listname += '{0} - {1} {2}\n'.format(i,
                                                       info['first_name'], 
                                                       info['last_name'])
                    i += 1
            vk_session.method('messages.send', {'user_id' : user.id, 'random_id': get_random_id(), 'message': 'Список \n' + listname + 'Доступные роли: user, head, admin, test \n`Роль номер',
                                                'keyboard': keyboard.get_keyboard()})
            user.work('reRole')
    else:
        if user.lastCommand == 'Spam':
            if not command in ['Отмена', 'отмена']:
                with sqlite3.connect(__DB__) as db:
                    cursor = db.cursor()
                    cursor.execute(
                        'SELECT `id` FROM `users` WHERE `mailing`=? and `id`<>?', (1,user.id))
                    user_ids = cursor.fetchall()
                    for user_id in user_ids:
                        vk_session.method('messages.send', {
                            'user_id': user_id, 'random_id': get_random_id(), 'message': command})
                    vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                    ), 'message': 'Сообщения успешно всем отправлены', 'keyboard': user.createKeyboard().get_keyboard()})
            else:
                vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                ), 'message': 'Ожидаю другие приказы!', 'keyboard': user.createKeyboard().get_keyboard()})
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
                with sqlite3.connect(__DB__) as db:
                    cursor = db.cursor()
                    cursor.execute(
                        'SELECT * FROM `subscriber` WHERE `number`=?', (number,))
                    result = cursor.fetchone()
                    cursor.execute('UPDATE `users` SET `status`=? WHERE `id`=?',(role, result[0]))
                    db.commit()
                    vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                    ), 'message': '{0} успешно получил {1}'.format(result[1], role), 'keyboard': user.createKeyboard().get_keyboard()})
            else:
                vk_session.method('messages.send', {'user_id': user.id, 'random_id': get_random_id(
                ), 'message': 'Жду другие команды!', 'keyboard': user.createKeyboard().get_keyboard()})
            user.work(None)

def run(info):
    user = Users(info['id'])
    commands(command=info['content']['message'], user=user)
    if user.status in __ADMINGROUP__:
        commands_plus(command=info['content']['message'], user=user)
