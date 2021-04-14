import time
from pynput import mouse

from client.base_listener import BaseListener


class MouseListener(BaseListener):

    def __init__(self, user_id, session_id):
        super().__init__(user_id, session_id, mouse.Listener(on_move=self.on_move, on_scroll=self.on_scroll))
        self.motion_list = []
        self.scroll_list = []

    def start_listening(self):
        self.listener.start()

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