from pynput import mouse
from pynput import keyboard
from common.logger import get_logger
from common import config
import time


class MouseListener:

    def __init__(self, user_id, session_id):
        self.session_id = session_id
        self.user_id = user_id
        self.motion_list = []
        self.scroll_list = []
        self.logger = get_logger('MouseListener')

    def start_listening(self):
        mouse_listener = mouse.Listener(on_move=self.on_move, on_scroll=self.on_scroll)
        mouse_listener.start()
        self.logger.debug('Mouse Listener has started')

    def on_move(self, x, y):
        time_moved = int(time.time())
        self.logger.debug(f'Pointer moved to {x}, {y}. Current time: {time_moved}')
        self.motion_list.append([self.user_id, self.session_id, time_moved, x, y])

    def on_scroll(self, x, y, dx, dy):
        time_scrolled = int(time.time())
        rotation = -1 if dy < 0 else 1
        self.logger.debug(f'Scrolled at {x} {y} {"down" if dy < 0 else "up"}. Current time: {time_scrolled}')
        self.scroll_list.append([self.user_id, self.session_id, time_scrolled, x, y, rotation])

    def get_motion_list(self):
        return self.motion_list

    def get_scroll_list(self):
        return self.scroll_list

    def clear_motion_list(self):
        self.motion_list.clear()

    def clear_scroll_list(self):
        self.scroll_list.clear()


class KeyboardListener:
    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id
        self.logger = get_logger('KeyboardListener')
        self.keys_pressed = {}
        self.keystroke_list = []

    def start_listening(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        keyboard_listener.start()
        self.logger.debug('Keyboard Listener has started')

    def on_press(self, key):
        time_pressed = int(time.time())
        try:
            self.logger.debug(f'alphanumeric key {key.vk} pressed')
            self.keys_pressed[key.vk] = time_pressed
        except AttributeError:
            self.logger.debug(f'special key {key.value.vk} pressed')
            self.keys_pressed[key.value.vk] = time_pressed

    def on_release(self, key):
        time_released = int(time.time())
        keycode = None
        try:
            keycode = key.vk
        except AttributeError:
            keycode = key.value.vk
        finally:
            self.logger.debug(f'{keycode} released')
            self.keystroke_list.append([self.user_id, self.session_id, self.keys_pressed.pop(keycode),
                                        time_released, keycode])

    def get_keystroke_list(self):
        return self.keystroke_list

    def clear_keystroke_list(self):
        self.keystroke_list.clear()


class Listener:

    def __init__(self, user_id, session_id):
        self.session_id = session_id
        self.user_id = user_id
        self.mouse_listener = None
        self.keyboard_listener = None

    def start_listening(self):
        self.mouse_listener = MouseListener(self.user_id, self.session_id)
        self.keyboard_listener = KeyboardListener(self.user_id, self.session_id)
        self.mouse_listener.start_listening()
        self.keyboard_listener.start_listening()

    def get_action_list(self, action_type):
        headers = config.CSV_HEADERS
        actions_dict = {'motion.csv': {'list': self.mouse_listener.get_motion_list(), 'header': headers['MOTION_HEADER']},
                        'scroll.csv': {'list': self.mouse_listener.get_scroll_list(), 'header': headers['SCROLL_HEADER']},
                        'keystroke.csv': {'list': self.keyboard_listener.get_keystroke_list(),
                                          'header': headers['KEYSTROKE_HEADER']}}
        return actions_dict[action_type]

    def clear_action_list(self):
        self.mouse_listener.clear_motion_list()
        self.mouse_listener.clear_scroll_list()
        self.keyboard_listener.clear_keystroke_list()


if __name__ == '__main__':
    kblsn = KeyboardListener(1, 2)
