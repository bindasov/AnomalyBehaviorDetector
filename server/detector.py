from listeners import Listener
from server.common.csv_helper import CSVHelper
from ml_worker import MLWorker
from server.common.conf import config
from server.common.logger import get_logger
import argparse
import time
import uuid


class Initializer:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Detector script')
        self.parser.add_argument('--uid', action="store", dest="user_id")

    def generate_session_id(self):
        return uuid.uuid1().int % (10 ** 12)

    def __get_user_id(self):

        if self.parser.parse_args().user_id is not None:
            return int(self.parser.parse_args().user_id)
        else:
            return None

    def parse_args(self,):
        return self.__get_user_id()


class DataHandler:
    def __get_data_to_learn(self, df, dataset_header):
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

    def prepare_data_for_ml(self, dataset_path, dataset_header, logger):
        df = CSVHelper().read_from_csv(csv_name=dataset_path)
        try:
            user, data_to_learn = self.__get_data_to_learn(df, dataset_header)
        except IndexError as e:
            logger.error(f"Could't read file with base dataset. Error: {e}")
        else:
            data_to_check = self.get_data_to_check(dataset_path)
            if data_to_check is not None:
                return data_to_check[dataset_header[1:]], data_to_learn, user
            else:
                return None, None, None


class Detector:
    def __init__(self):
        self.users_list = []
        self.user_id_result = []
        self.logger = get_logger('Detector')
        self.detect_types = {0: 'motion', 1: 'scroll', 2: 'keystroke'}
        self.data_handler = DataHandler()

    def __make_identification(self, data_to_learn, user, data_to_check):
        if not data_to_check.empty:
            result_list = MLWorker().forest(data_to_learn, user, data_to_check).tolist()
            return max(set(result_list), key=result_list.count)

    def detect(self, user_id):
        for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
            data_to_check, data_to_learn, user = self.data_handler.prepare_data_for_ml(dataset_path,
                                                                                       dataset_header, self.logger)

            if data_to_check is not None:
                self.users_list.append(user.to_list())
                self.user_id_result.append(self.__make_identification(data_to_learn, user, data_to_check))

        self.users_list = self.data_handler.get_unique_users_list(self.users_list)

        user_id_result = [result for result in self.user_id_result if result is not None]

        if user_id is None and user_id_result:
            print(f'User ID is not set. User ID list: {self.user_id_result}. The most similar user is '
                  f'{max(set(user_id_result), key=user_id_result.count)}')
        elif user_id in user_id_result:
            correct_type_ids = [index for index, value in enumerate(self.user_id_result) if value == user_id]
            print(f'OK. User {user_id}. User ID result: {self.user_id_result}. '
                  f'Number of classifiers that confirm current user: {self.user_id_result.count(user_id)}. '
                  f'Detected by: {[self.detect_types[d_type] for d_type in correct_type_ids]}')
            for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
                CSVHelper().write_to_csv(csv_name=dataset_path, columns=dataset_header,
                                         actions_list=self.data_handler.get_data_to_check(dataset_path))
        elif user_id_result:
            print(f'Unknown user! User id result: {self.user_id_result}, user id: {repr(user_id)}')
            if user_id not in self.users_list:
                for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
                    CSVHelper().write_to_csv(csv_name=dataset_path, columns=dataset_header,
                                             actions_list=self.data_handler.get_data_to_check(dataset_path))

        listener.clear_action_list()
        self.user_id_result.clear()
        self.users_list.clear()


if __name__ == '__main__':
    initializer = Initializer()
    user_id = initializer.parse_args()
    session_id = Initializer().generate_session_id()
    listener = Listener(user_id, session_id)
    listener.start_listening()
    print(f'Started listening. User ID: {user_id}, session ID: {session_id}')

    detector = Detector()
    while True:
        time.sleep(config.SLEEP_TIME)
        detector.detect(user_id)
