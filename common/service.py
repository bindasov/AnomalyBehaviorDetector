import pickle
import zmq
import signal


class BaseServiceServer:
    _SOCKET = None

    def __init__(self, logger):
        self.logger = logger
        _ctx = zmq.Context()
        self.socket = _ctx.socket(zmq.REP)
        self.socket.bind(self._SOCKET)

    def _get_data(self):
        return pickle.loads(self.socket.recv())

    def _send_result(self, result):
        return self.socket.send(pickle.dumps(result))

    def do_task(self, data: dict):
        raise NotImplementedError('Need to implement in subclass')

    def exit_gracefully(self, signum, frame):
        raise NotImplementedError('Need to implement in subclass')

    def serve(self):
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        while True:
            _result = {}
            try:
                _data = self._get_data()
                if _data:
                    _result = self.do_task(_data)
                else:
                    _result = {'error': 'Cannot load data'}
            except Exception as e:
                _msg = f'An error occurred: {e}'
                self.logger.error(_msg)
                _result = {'error': _msg}
            finally:
                self._send_result(_result)
