from listeners import Listener
from common.csv_helper import CSVHelper
import os


def generate_session_id():
    session_column = CSVHelper().read_from_csv('session')
    if session_column is not None:
        return max(session_column) + 1
    else:
        return 0


def get_user_id():
    return abs(hash(os.getlogin())) % (10 ** 8)


if __name__ == '__main__':
    user_id = get_user_id()
    session_id = generate_session_id()
    listener = Listener(user_id, session_id)
    listener.start_listening()
