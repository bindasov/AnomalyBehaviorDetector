from abc import ABC, abstractmethod


class BaseListener(ABC):

    def __init__(self, session_id, listener):
        self.session_id = session_id
        self.listener = listener

    @abstractmethod
    def start_listening(self):
        pass
