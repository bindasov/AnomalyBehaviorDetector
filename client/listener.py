from time import sleep
import uuid

from common.tasks import ClientTask
from common.logger import get_logger
from common import config
from client.keyboard_listener import KeyboardListener
from client.mouse_listener import MouseListener

logger = get_logger('client-listener')


def generate_session_id():
    return uuid.uuid1().int % (10 ** 12)


class Listener:

    def __init__(self, session_id):
        self.session_id = session_id
        self.mouse_listener = MouseListener(self.session_id)
        self.keyboard_listener = KeyboardListener(self.session_id)

    def start_listening(self):
        self.mouse_listener.start_listening()
        self.keyboard_listener.start_listening()

    def get_action_list(self, action_type):
        actions_dict = {
            'motion': self.mouse_listener.get_motion_list(),
            'scroll': self.mouse_listener.get_scroll_list(),
            'keystroke': self.keyboard_listener.get_keystroke_list()}
        return actions_dict[action_type]

    def clear_action_list(self):
        self.mouse_listener.clear_motion_list()
        self.mouse_listener.clear_scroll_list()
        self.keyboard_listener.clear_keystroke_list()


if __name__ == '__main__':
    mode = int(input('Mode (0 - learn, 1 - operating): '))
    uid = input('ID: ')
    session = generate_session_id()

    logger.info('Starting client listener')
    listener = Listener(session)
    listener.start_listening()

    while True:
        sleep(config.SLEEP_TIME)
        for action_type in config.DATASETS.keys():
            action_list = listener.get_action_list(action_type)
            if action_list:
                if mode:
                    res = ClientTask(config.SERVICE_ADDR).authenticate_user(uid, action_type, action_list)
                else:
                    res = ClientTask(config.SERVICE_ADDR).send_training_data(uid, action_type, action_list)
                logger.info(f'Server response: {res}')
        listener.clear_action_list()
