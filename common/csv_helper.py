import os
import pandas as pd
from common.logger import get_logger


class CSVHelper:

    def __init__(self):
        self.logger = get_logger('CSV-helper')

    @staticmethod
    def __file_exists(filename):
        return os.path.isfile(filename)

    @staticmethod
    def list_to_pd_dataframe(data_list, columns=None):
        try:
            return pd.DataFrame(data_list, columns=columns)
        except ValueError:
            pass

    def write_to_csv(self, actions_list, csv_name, columns):
        row = self.list_to_pd_dataframe(actions_list['list'], columns=columns)
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
