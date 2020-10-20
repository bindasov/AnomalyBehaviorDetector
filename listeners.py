from pynput import mouse
from pynput import keyboard
from common.csv_helper import CSVHelper
from common.logger import get_logger
from common.conf import config
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


class KeyboardListener:
    LOOKUP_SPECIAL_KEY = {keyboard.Key.alt: 'alt', keyboard.Key.alt_l: 'altleft', keyboard.Key.alt_r: 'altright',
                          keyboard.Key.alt_gr: 'altright', keyboard.Key.backspace: 'backspace',
                          keyboard.Key.caps_lock: 'capslock', keyboard.Key.cmd: 'winleft',
                          keyboard.Key.cmd_r: 'winright', keyboard.Key.ctrl: 'ctrlleft',
                          keyboard.Key.ctrl_r: 'ctrlright', keyboard.Key.delete: 'delete', keyboard.Key.down: 'down',
                          keyboard.Key.end: 'end', keyboard.Key.enter: 'enter', keyboard.Key.esc: 'esc',
                          keyboard.Key.f1: 'f1', keyboard.Key.f2: 'f2', keyboard.Key.f3: 'f3', keyboard.Key.f4: 'f4',
                          keyboard.Key.f5: 'f5', keyboard.Key.f6: 'f6', keyboard.Key.f7: 'f7', keyboard.Key.f8: 'f8',
                          keyboard.Key.f9: 'f9', keyboard.Key.f10: 'f10', keyboard.Key.f11: 'f11',
                          keyboard.Key.f12: 'f12', keyboard.Key.home: 'home', keyboard.Key.left: 'left',
                          keyboard.Key.page_down: 'pagedown', keyboard.Key.page_up: 'pageup',
                          keyboard.Key.right: 'right', keyboard.Key.shift: 'shift_left',
                          keyboard.Key.shift_r: 'shiftright', keyboard.Key.space: 'space', keyboard.Key.tab: 'tab',
                          keyboard.Key.up: 'up', keyboard.Key.media_play_pause: 'playpause',
                          keyboard.Key.insert: 'insert', keyboard.Key.num_lock: 'num_lock', keyboard.Key.pause: 'pause',
                          keyboard.Key.print_screen: 'print_screen', keyboard.Key.scroll_lock: 'scroll_lock'}

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


class Listener:

    def __init__(self, user_id, session_id):
        self.session_id = session_id
        self.user_id = user_id
        self.m_listener = None
        self.k_listener = None

    def start_listening(self):
        self.m_listener = MouseListener(self.user_id, self.session_id)
        self.k_listener = KeyboardListener(self.user_id, self.session_id)
        self.m_listener.start_listening()
        self.k_listener.start_listening()

    def get_action_list(self, action_type):
        headers = config.CSV_HEADERS
        actions_dict = {'motion.csv': {'list': self.m_listener.get_motion_list(), 'header': headers['MOTION_HEADER']},
                        'scroll.csv': {'list': self.m_listener.get_scroll_list(), 'header': headers['SCROLL_HEADER']},
                        'keystroke.csv': {'list': self.k_listener.get_keystroke_list(),
                                          'header': headers['KEYSTROKE_HEADER']}}
        return actions_dict[action_type]


if __name__ == '__main__':
    kblsn = KeyboardListener(1, 2)
