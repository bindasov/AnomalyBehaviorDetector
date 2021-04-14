import sys

from common.service import BaseServiceServer
from common.logger import get_logger
from common import config
from common.csv_helper import CSVHelper
from server.detector import Detector


class SocketTaskController:
    def __init__(self):
        self.logger = get_logger('task-controller')

    def record_learn_data(self, data):
        self.logger.debug('Writing actions to file in learn mode')
        try:
            CSVHelper().write_to_csv(csv_name='logs/' + data['type'] + '.csv', actions_list=data['data'],
                                     columns=config.HEADERS[data['type']])
        except Exception as e:
            return {'result': 1, 'error': e}
        else:
            return {'result': 0}

    def launch_detector(self, data):
        self.logger.debug('Detecting user in operating mode')
        return {'result': 0, 'user': Detector().detect(data)}


class SocketServerService(BaseServiceServer):
    _SOCKET = config.SERVICE_ADDR

    def __init__(self):
        super().__init__(logger=get_logger('detector-service'))
        self._controller = SocketTaskController()

    def exit_gracefully(self, signum, frame):
        sys.exit()

    def do_task(self, data: dict):
        if 'mode' not in data or 'type' not in data or 'data' not in data:
            self.logger.error(f'Broken data: {data}')
            return None
        elif data['mode'] == 0:
            return self._controller.record_learn_data(data)
        else:
            return self._controller.launch_detector(data)


if __name__ == '__main__':
    logger = get_logger('Detector-server')
    logger.info('Starting Detector server')
    SocketServerService().serve()
