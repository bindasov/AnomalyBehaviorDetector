import sys

from common.service import BaseServiceServer
from common.logger import get_logger
from common import config
from common.helpers import DataHandler
from server.detector import Detector


class SocketTaskController:
    def __init__(self):
        self.logger = get_logger('task-controller')

    def record_training_data(self, data):
        self.logger.debug('Recording training data')
        return DataHandler().record_data(data)

    def launch_detector(self, data):
        self.logger.debug('Detecting user in operating mode')
        try:
            user = Detector().detect(data['type'], data['uid'], data['actions'])
        except Exception as e:
            self.logger.error(f'User detection failed. Error: {e}')
            self.logger.error(data['type'], data['uid'], data['actions'])
            return {'result': 1, 'error': e}
        return {'result': 0, 'user': user}


class SocketServerService(BaseServiceServer):
    _SOCKET = config.SERVICE_ADDR

    def __init__(self):
        super().__init__(logger=get_logger('detector-service'))
        self._controller = SocketTaskController()

    def exit_gracefully(self, signum, frame):
        sys.exit()

    def do_task(self, data: dict):
        if 'mode' not in data or 'type' not in data or 'actions' not in data:
            self.logger.error(f'Broken data: {data}')
            return None
        elif data['mode'] == 0:
            return self._controller.record_training_data(data)
        else:
            return self._controller.launch_detector(data)


if __name__ == '__main__':
    logger = get_logger('Detector-server')
    logger.info('Starting Detector server')
    SocketServerService().serve()
