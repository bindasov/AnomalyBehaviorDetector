from enum import Enum, IntEnum


class LoggerLevels(IntEnum):
    debug = 10
    info = 20
    warning = 30
    error = 40
    critical = 50


class ActionTypes(str, Enum):
    motion = 'motion'
    scroll = 'scroll'
    keystroke = 'keystroke'
