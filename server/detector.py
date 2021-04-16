from server.ml_worker import forest
from common import config
from common.logger import get_logger
from common.helpers import DataHandler


class Detector:
    def __init__(self):
        self.users_list = []
        self.user_data = {}
        self.logger = get_logger('Detector')

    def make_identification(self, training_data, user, action_data):
        result_list = forest(training_data, user, action_data).tolist()
        return max(set(result_list), key=result_list.count)

    def detect(self, type, user_id, action_data):
        dataset_path = config.LOGS_FOLDER + type + config.DATASET_EXTENSION
        user, training_data = DataHandler().prepare_training_data(dataset_path, config.DATASETS[type])

        if action_data is not None:
            self.users_list.append(user.to_list())
            ml_result = self.make_identification(training_data, user, action_data)

            if user_id == ml_result:
                self.logger.info(f'OK. User is correct. Detected by {type}')
                self.user_data['actions'] = action_data
                self.user_data['uid'] = user_id
                self.user_data['type'] = type
                DataHandler().record_data(self.user_data)
                return True
            else:
                self.logger.info(f'User ID {user_id}, detected user by ml: {ml_result}')
                return False
        else:
            return {'result': 1, 'error': 'empty action data'}
