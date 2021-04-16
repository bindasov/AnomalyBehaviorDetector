import os
import pandas as pd

from common.logger import get_logger
from common import config


class CSVHelper:

    def __init__(self):
        self.logger = get_logger('CSV-helper')

    @staticmethod
    def __file_exists(filename):
        return os.path.isfile(filename)

    @staticmethod
    def list_to_pd_dataframe(data_list, columns=None):
        try:
            return pd.DataFrame.from_records(data=data_list, columns=columns)
        except ValueError:
            return None

    @staticmethod
    def pd_dataframe_to_list(df):
        return df.values.tolist()

    def write_to_csv(self, actions_list, csv_name, columns):
        row = self.list_to_pd_dataframe(actions_list, columns=columns)
        if not self.__file_exists(csv_name):
            self.logger.debug(f'Writing to a new file {csv_name}')
            row.to_csv(csv_name, index=False)
        else:
            self.logger.debug(f'Writing to existing file {csv_name}')
            row.to_csv(csv_name, mode='a', header=False, index=False)

    def read_from_csv(self, csv_name, column_name=None, columns=None):
        if self.__file_exists(csv_name):
            self.logger.debug(f'Reading from {csv_name}')
            df = pd.read_csv(csv_name, usecols=columns)
            self.logger.debug(f'Successfully read from {csv_name}')
            if column_name:
                return df[column_name]
            else:
                return df
        return None


class DataHandler:
    def __init__(self):
        self.logger = get_logger('data-handler')

    def __get_training_data(self, df, dataset_header):
        return df[dataset_header[0]], df[dataset_header[1:]]

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

    def insert_value_into_every_list_in_data(self, data, value, position):
        for index, list_element in enumerate(data):
            list_element.insert(position, value)
            data[index] = list_element
        return data

    def record_data(self, data):
        data['actions'] = DataHandler().insert_value_into_every_list_in_data(data['actions'], data['uid'], 0)
        self.logger.debug('Writing actions to file in learn mode')
        try:
            CSVHelper().write_to_csv(csv_name=config.LOGS_FOLDER + data['type'] + config.DATASET_EXTENSION,
                                     actions_list=data['actions'], columns=config.DATASETS[data['type']])
        except Exception as e:
            self.logger.error(f'Could not record action data. Error {e}')
            return {'result': 1, 'error': e}
        else:
            return {'result': 0}
