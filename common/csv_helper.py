import pandas as pd
import os
from common.logger import get_logger


class CSVHelper:

    def __init__(self):
        self.FIELDNAMES = ['user', 'session', 'type', 'x', 'y', 'time']
        self.logger = get_logger('CSVHelper')

    def __file_exists(self, filename):
        return os.path.isfile(filename)

    def list_to_pd_dataframe(self, data_list, columns=None):
        return pd.DataFrame(data_list, columns=columns)

    def write_to_csv(self, actions_list, csv_name, columns):
        row = self.list_to_pd_dataframe(actions_list, columns=columns)
        if not self.__file_exists(csv_name):
            self.logger.debug(f'Writing to a new file {csv_name}')
            row.to_csv(csv_name, index=False)
            self.logger.debug(f'Successfully written to {csv_name}')
        else:
            self.logger.debug(f'Writing to existing file {csv_name}')
            row.to_csv(csv_name, mode='a', header=False, index=False)
            self.logger.debug(f'Successfully written to {csv_name}')

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


if __name__ == '__main__':
    csv_helper = CSVHelper()
