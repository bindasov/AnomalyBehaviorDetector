import os
from time import sleep

from common.tasks import ClientTask
from common import config
from client.keyboard_listener import KeyboardListener
from client.mouse_listener import MouseListener


class Listener:

    def __init__(self, user_id, session_id):
        self.session_id = session_id
        self.user_id = user_id
        self.mouse_listener = MouseListener(self.user_id, self.session_id)
        self.keyboard_listener = KeyboardListener(self.user_id, self.session_id)

    def start_listening(self):
        self.mouse_listener.start_listening()
        self.keyboard_listener.start_listening()

    def get_action_list(self, action_type):
        actions_dict = {
            'motion': {'list': self.mouse_listener.get_motion_list(), 'header': config.HEADERS['motion']},
            'scroll': {'list': self.mouse_listener.get_scroll_list(), 'header': config.HEADERS['scroll']},
            'keystroke': {'list': self.keyboard_listener.get_keystroke_list(),
                          'header': config.HEADERS['keystroke']}}
        return actions_dict[action_type]

    def clear_action_list(self):
        self.mouse_listener.clear_motion_list()
        self.mouse_listener.clear_scroll_list()
        self.keyboard_listener.clear_keystroke_list()


if __name__ == '__main__':
    mode = int(input('Mode (0 - learn, 1 - operating): '))
    uid = input('ID: ')
    session = input('Session: ')

    action_types = ['scroll', 'motion', 'keystroke']

    listener = Listener(uid, session)
    listener.start_listening()

    if not os.path.exists(config.LOGS_FOLDER):
        os.makedirs(config.LOGS_FOLDER)

    print('Working...')
    while True:
        sleep(config.SLEEP_TIME)
        for action in action_types:
            action_list = listener.get_action_list(action)
            if mode:
                res = ClientTask(config.SERVICE_ADDR).recognize_user(uid, action, action_list)
            else:
                res = ClientTask(config.SERVICE_ADDR).send_learn_data(action, action_list)
            print(res)
            # try:
            #     CSVHelper().write_to_csv(lst, f'{config.LOGS_FOLDER}/{action}.csv', config.HEADERS[action])
            # except Exception:
            #     continue
        listener.clear_action_list()
