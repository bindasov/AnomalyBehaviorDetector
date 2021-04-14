from abc import ABC, abstractmethod


class BaseListener(ABC):

    def __init__(self, user_id, session_id, listener):
        self.user_id = user_id
        self.session_id = session_id
        self.listener = listener

    @abstractmethod
    def start_listening(self):
        pass
