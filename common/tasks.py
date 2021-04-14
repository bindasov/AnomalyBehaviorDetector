from pickle import dumps, loads
import zmq


from common.logger import get_logger

# __ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(__ROOT)


class BaseTask:
    def __init__(self, address, logger=None):
        self.server_address = address
        self.logger = logger or get_logger('TaskWorker')
        self.context = zmq.Context()

    def _connect(self):
        try:
            socket = self.context.socket(zmq.REQ)
            self.logger.debug(f'Connecting to {self.server_address}')
            socket.connect(self.server_address)
        except Exception as e:
            self.logger.error(f'Connect exception: {e}')
            return None
        else:
            self.logger.debug(f'Connected to {self.server_address}')
            return socket

    def _stop(self):
        self.context.destroy()

    def _send_task(self, data):
        socket = self._connect()
        if socket is None:
            res = None
        else:
            socket.send(dumps(data))
            res = loads(socket.recv())
        self._stop()
        return res


class ClientTask(BaseTask):

    def send_learn_data(self, actions_type, actions_log):
        return self._send_task(data={'mode': 0, 'type': actions_type, 'data': actions_log})

    def recognize_user(self, uid, actions_type, actions_log):
        return self._send_task(data={'mode': 1, 'uid': uid, 'type': actions_type, 'data': actions_log})
