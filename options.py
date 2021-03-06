import sqlite3

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


__VERSION__ = 5.126
__DB__ = 'vk.db'
__ADMINGROUP__ = ['admin', 'head', 'test']
__DEBUGMODE__ = True
__POSTFILTERS__ = ['Новости', 'Домашняя работа', 'Контрольные']
__ANSWER__ = '8de15fe6'

def POSTFILTERS():
    i = 1
    text = ''
    for post in __POSTFILTERS__:
        text+= str(i) + ' - ' + post + '\n'
        i+=1
    return text

class Users:
    def __init__(self, id):
        self.id = id
        db = sqlite3.connect(__DB__)
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM `users` WHERE `id`=?',
                            (self.id,))
            result = cursor.fetchone()
            self.status = result[1]
            self.mailing = result[2]
            self.lastCommand = result[3]
            self.postFilter = []
            for symbol in result[4]: 
                self.postFilter.append(__POSTFILTERS__[int(symbol)-1])
        except:
            self.status = 'user'
            self.mailing = 1
            self.lastCommand = None
            self.postFilter = []
            cursor.execute('INSERT INTO `users`(`id`, `status`, `mailing`,`post_filters`) VALUES (?,?,?,?)',
                            (self.id, self.status, self.mailing, ''))
            db.commit()
        db.close()

    def checkWork(self):
        return self.lastCommand

    def work(self, command):
        self.lastCommand = command
        db = sqlite3.connect(__DB__)
        cursor = db.cursor()
        cursor.execute(
            'UPDATE `users` SET `last_command`=? WHERE `id`=?', (self.lastCommand, self.id))
        db.commit()
        db.close()

    def reSpam(self):
        self.mailing = -1 if self.mailing == 1 else self.mailing + 2
        db = sqlite3.connect(__DB__)
        cursor = db.cursor()
        cursor.execute(
            'UPDATE `users` SET `mailing`=? WHERE `id`=?', (self.mailing, self.id))
        db.commit()
        db.close()

    def reFilter(self, listfilter):
        self.postFilter = []
        sql = ''
        for symbol in listfilter:
            self.postFilter.append(__POSTFILTERS__[int(symbol)-1])
            sql += str(int(symbol))
        with sqlite3.connect(__DB__) as db:
            cursor = db.cursor()
            cursor.execute(
                'UPDATE `users` SET `post_filters`=? WHERE `id`=?', (sql, self.id))
            db.commit()
        
    def colorSpam(self):
        if self.mailing == 1:
            return VkKeyboardColor.POSITIVE
        #if self.mailing == 0:
            #return VkKeyboardColor.PRIMARY
        if self.mailing == -1:
            return VkKeyboardColor.NEGATIVE

    def createKeyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Рассылка', color=self.colorSpam())
        keyboard.add_button('Фильтры')
        if self.status in __ADMINGROUP__:
            keyboard.add_line()
            keyboard.add_button('Массовая отправка')
            if self.status == 'admin':
                keyboard.add_line()
                keyboard.add_button('Изменить роль')
        return keyboard
    
    def getOtherUser(self, parametry = ''): 
        with sqlite3.connect(__DB__) as db:
            cursor = db.cursor()
            cursor.execute(
                'SELECT `id` FROM `users` WHERE `id`<>?'+ parametry, (self.id,))
            result = cursor.fetchall()
            users = []
            for user in result: users.append(user[0])
        return users

    def reStarus(self, role):
        with sqlite3.connect(__DB__) as db:
            cursor = db.cursor()
            cursor.execute(
                'UPDATE `users` SET `status`=? WHERE `id`=?', (role, self.id))
            db.commit()
    
    def createdSubscribe(self, vk_session):
        listname = ''
        with sqlite3.connect(__DB__) as db:
            cursor = db.cursor()
            cursor.execute('SELECT `id` FROM `users` WHERE `id`<>?',(self.id,))
            result = cursor.fetchall()
            cursor.execute('DELETE FROM `subscriber`')
            i = 1
            for subscriber in result:
                info = vk_session.method('users.get', {'user_ids': subscriber[0], 'name_case': 'Nom'})[0]
                cursor.execute('INSERT INTO `subscriber` VALUES (?,?)',(subscriber[0],i))
                db.commit()
                listname += '{0} - {1} {2}\n'.format(i, info['first_name'], info['last_name'])
                i += 1
        return listname

class Events:
    def __init__(self, type, event):
        self.type = type
        self.event = event

    def message(self):
        return {'id': self.event['message']['from_id'], 'content': {'message': self.event['message']['text']}}
    
    def wall(self):
        return {'id': '{}_{}'.format(self.event['owner_id'], self.event['id']), 'content': {'text': self.event['text'], 'attachment': self.event['attachments']}}

class Walls:
    def __init__(self, id):
        self.id = id
        self.title = None
    
    def handling(self, content):
        text = content['text']
        for i in range(len(__POSTFILTERS__)):
            if text.find(__POSTFILTERS__[i]) != -1:
                self.title = str(i + 1)
        self.text = text[text.find('\n'):]
        self.files = []
        if content.get('attachment'):
            for file in content['attachment']:
                if file['type'] in ['photo', 'doc', 'poll']:
                    self.files.append({'type': file['type'], 'id': '{0}_{1}'.format(
                        file[file['type']]['owner_id'], file[file['type']]['id']), })
    def message(self):
        message = {}
        
        if len(self.text) > 0: message['message'] = self.text
        if len(self.files) > 0:
            message['attachment'] = ''
            for file in self.files:
                message['attachment'] += file['type'] + file['id'] +','
            else:
                message['attachment'] = message['attachment'][:-1]
        return message
