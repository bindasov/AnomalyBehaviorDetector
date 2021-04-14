import time
from pynput import keyboard

from client.base_listener import BaseListener


class KeyboardListener(BaseListener):

    def __init__(self, session_id):
        super().__init__(session_id, keyboard.Listener(on_press=self.on_press, on_release=self.on_release))
        self.keys_pressed = {}
        self.keystroke_list = []

    def start_listening(self):
        self.listener.start()

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
                self.keystroke_list.append([self.session_id, self.keys_pressed.pop(keycode), time_released, keycode])
            except KeyError:
                pass

    def get_keystroke_list(self):
        return self.keystroke_list

    def clear_keystroke_list(self):
        self.keystroke_list.clear()
