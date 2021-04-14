from listeners import Listener
from common.csv_helper import CSVHelper
from ml_worker import MLWorker
from common import config
from common.logger import get_logger
import argparse
import time
import uuid


def generate_session_id():
    return uuid.uuid1().int % (10 ** 12)


class Initializer:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Detector script')
        self.parser.add_argument('--uid', action="store", dest="user_id")

    def __get_user_id(self):

        if self.parser.parse_args().user_id is not None:
            return int(self.parser.parse_args().user_id)
        else:
            return None

    def parse_args(self,):
        return self.__get_user_id()


class DataHandler:
    def __init__(self):
        self.logger = get_logger('data-handler')

    def __get_training_data(self, df, dataset_header):
        return df[dataset_header[0]], df[dataset_header[1:]]

    def get_data_to_check(self, dataset_path):
        dataset_path_split = dataset_path.split('/')

        if len(dataset_path_split) < 2:
            dataset_name = dataset_path
        else:
            dataset_name = dataset_path_split[1]

        action_dict = listener.get_action_list(dataset_name)
        return CSVHelper().list_to_pd_dataframe(data_list=action_dict['list'], columns=action_dict['header'])

    def get_unique_users_list(self, users_list):
        for index, lst in enumerate(users_list):
            users_list[index] = list(set(lst))
        flat_list = [item for sublist in users_list for item in sublist]
        return list(set(flat_list))

    def prepare_training_data(self, dataset_path, dataset_header):
        df = CSVHelper().read_from_csv(csv_name=dataset_path)
        try:
            user, training_data = self.__get_training_data(df, dataset_header)
        except IndexError as e:
            self.logger.error(f"Could not read file with base dataset. Error: {e}")
            return None, None
        return user, training_data


class Detector:
    def __init__(self):
        self.users_list = []
        self.user_id_result = []
        self.logger = get_logger('Detector')
        self.data_handler = DataHandler()

    def __make_identification(self, training_data, user, action_data):
        result_list = MLWorker().forest(training_data, user, action_data).tolist()
        return max(set(result_list), key=result_list.count)

    def detect(self, type, user_id, action_data):
        dataset_path = config.LOGS_FOLDER + '/' + type + '.csv'
        user, training_data = self.data_handler.prepare_training_data(dataset_path, config.HEADERS[type])

        if action_data is not None:
            print(f'user: {user}')
            self.users_list.append(user.to_list())
            ml_result = self.__make_identification(training_data, user, action_data)
            self.user_id_result.append(ml_result)

        if user_id in self.user_id_result:
            print(f'OK. User is correct. Detected by {type}')
            CSVHelper().write_to_csv(csv_name=dataset_path, columns=config.HEADERS[type], actions_list=action_data)
            return {'result': 0, 'user': self.user_id_result}
        else:
            print(f'User ID {user_id}, detected user by ml: {self.user_id_result}')
            return {'result': 1, 'error': 'wrong user'}

        # self.users_list = self.data_handler.get_unique_users_list(self.users_list)
        #
        # user_id_result = [result for result in self.user_id_result if result is not None]
        #
        # if user_id is None and user_id_result:
        #     print(f'User ID is not set. User ID list: {self.user_id_result}. The most similar user is '
        #           f'{max(set(user_id_result), key=user_id_result.count)}')
        # elif user_id in user_id_result:
        #     correct_type_ids = [index for index, value in enumerate(self.user_id_result) if value == user_id]
        #     print(f'OK. User {user_id}. User ID result: {self.user_id_result}. '
        #           f'Number of classifiers that confirm current user: {self.user_id_result.count(user_id)}. '
        #           f'Detected by: {[self.detect_types[d_type] for d_type in correct_type_ids]}')
        #     for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
        #         CSVHelper().write_to_csv(csv_name=dataset_path, columns=dataset_header,
        #                                  actions_list=self.data_handler.get_data_to_check(dataset_path))
        # elif user_id_result:
        #     print(f'Unknown user! User id result: {self.user_id_result}, user id: {repr(user_id)}')
        #     if user_id not in self.users_list:
        #         for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
        #             CSVHelper().write_to_csv(csv_name=dataset_path, columns=dataset_header,
        #                                      actions_list=self.data_handler.get_data_to_check(dataset_path))
        #
        # listener.clear_action_list()
        # self.user_id_result.clear()
        # self.users_list.clear()


if __name__ == '__main__':
    initializer = Initializer()
    user_id = initializer.parse_args()
    session_id = generate_session_id()
    listener = Listener(user_id, session_id)
    listener.start_listening()
    print(f'Started listening. User ID: {user_id}, session ID: {session_id}')

    detector = Detector()
    while True:
        time.sleep(config.SLEEP_TIME)
        detector.detect(user_id)
