from common.base import LoggerLevels


HEADERS = {"motion": ["user", "session", "time", "x", "y"],
           "scroll": ["user", "session", "time", "x", "y", "rotation"],
           "keystroke": ["user", "session", "timepress", "timerelease", "keycode"]}

SLEEP_TIME = 5
LOGS_FOLDER = 'logs'

LOGLEVEL = LoggerLevels.debug
LOG_FILE = None
SERVICE_ADDR = 'tcp://127.0.0.1:4999'
