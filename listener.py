from pynput import mouse
from pynput import keyboard
import time
import pandas as pd
import os
# import argparse

from time import sleep


class CSVHelper:

    def __init__(self):
        self.FIELDNAMES = ['user', 'session', 'type', 'x', 'y', 'time']

    @staticmethod
    def __file_exists(filename):
        return os.path.isfile(filename)

    @staticmethod
    def list_to_pd_dataframe(data_list, columns=None):
        try:
            return pd.DataFrame(data_list, columns=columns)
        except ValueError:
            pass

    def write_to_csv(self, actions_list, csv_name, columns):
        row = self.list_to_pd_dataframe(actions_list['list'], columns=columns)
        if not self.__file_exists(csv_name):
            row.to_csv(csv_name, index=False)
        else:
            row.to_csv(csv_name, mode='a', header=False, index=False)


class MouseListener:

    def __init__(self, user_id, session_id):
        self.session_id = session_id
        self.user_id = user_id
        self.motion_list = []
        self.scroll_list = []

    def start_listening(self):
        mouse_listener = mouse.Listener(on_move=self.on_move, on_scroll=self.on_scroll)
        mouse_listener.start()

    def on_move(self, x, y):
        time_moved = int(time.time())
        self.motion_list.append([self.user_id, self.session_id, time_moved, x, y])

    def on_scroll(self, x, y, dx, dy):
        time_scrolled = int(time.time())
        rotation = -1 if dy < 0 else 1
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
        self.keys_pressed = {}
        self.keystroke_list = []

    def start_listening(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        keyboard_listener.start()

    def on_press(self, key):
        time_pressed = int(time.time())
        try:
            self.keys_pressed[key.vk] = time_pressed
        except AttributeError:
            self.keys_pressed[key.value.vk] = time_pressed

    def on_release(self, key):
        time_released = int(time.time())
        keycode = None
        try:
            keycode = key.vk
        except AttributeError:
            keycode = key.value.vk
        finally:
            try:
                self.keystroke_list.append([self.user_id, self.session_id, self.keys_pressed.pop(keycode),
                                            time_released, keycode])
            except KeyError:
                pass

    def get_keystroke_list(self):
        return self.keystroke_list

    def clear_keystroke_list(self):
        self.keystroke_list.clear()


class Listener:
    HEADERS = {"motion": ["user", "session", "time", "x", "y"],
               "scroll": ["user", "session", "time", "x", "y", "rotation"],
               "keystroke": ["user", "session", "timepress", "timerelease", "keycode"]}

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
            'motion': {'list': self.mouse_listener.get_motion_list(), 'header': self.HEADERS['motion']},
            'scroll': {'list': self.mouse_listener.get_scroll_list(), 'header': self.HEADERS['scroll']},
            'keystroke': {'list': self.keyboard_listener.get_keystroke_list(),
                          'header': self.HEADERS['keystroke']}}
        return actions_dict[action_type]

    def clear_action_list(self):
        self.mouse_listener.clear_motion_list()
        self.mouse_listener.clear_scroll_list()
        self.keyboard_listener.clear_keystroke_list()


if __name__ == '__main__':
    uid = input('ID: ')
    session = input('Session: ')

    actions_list = ['scroll', 'motion', 'keystroke']

    listener = Listener(uid, session)
    listener.start_listening()

    if not os.path.exists('real_logs'):
        os.makedirs('real_logs')

    print('Working...')
    while True:
        sleep(15)
        for action in actions_list:
            lst = listener.get_action_list(action)
            try:
                CSVHelper().write_to_csv(lst, f'real_logs/{action}.csv', listener.HEADERS[action])
            except Exception:
                continue
        listener.clear_action_list()
