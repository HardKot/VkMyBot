from flask import Flask, request
#Модули с параметрами, классами
from options import Events, logging, __ANSWER__, CHECKDB, CREATEDB
#Модули для обработки
import communication
import wall


app = Flask(__name__)

@app.route("/", methods=['POST'])
def events():
    content = request.get_json()
    if content['type'] == 'confirmation':
        logging.INFO('Связь с группой %s успешно установленна',
                     content['group_id'])
        return __ANSWER__
    event = Events(content['type'], content['object'])
    if event.type == 'message_new':
        communication.run(event.message())
    elif event.type == 'wall_post_new':
        wall.run(event.wall())
    return 'ok'

if __name__ == '__main__':

    app.run()
