import pandas as pd
import os
from common.conf import config
from common.logger import get_logger


class CSVHelper:

    def __init__(self):
        self.FIELDNAMES = ['user', 'session', 'type', 'x', 'y', 'time']
        self.logger = get_logger('CSVHelper')

    def __file_exists(self, filename):
        return os.path.isfile(filename)

    def write_to_csv(self, actions_list, csv_name=config.DEFAULT_CSV, columns=config.DEFAULT_HEADER):
        row = pd.DataFrame(actions_list, columns=columns)
        if not self.__file_exists(csv_name):
            self.logger.debug(f'Writing to a new file {csv_name}')
            row.to_csv(csv_name, index=False)
            self.logger.debug(f'Successfully written to {csv_name}')
        else:
            self.logger.debug(f'Writing to existing file {csv_name}')
            row.to_csv(csv_name, mode='a', header=False, index=False)
            self.logger.debug(f'Successfully written to {csv_name}')

    def read_from_csv(self, csv_name=config.DEFAULT_CSV, column_name=None, usecols=config.DEFAULT_HEADER):
        if self.__file_exists(csv_name):
            self.logger.debug(f'Reading from {csv_name}')
            df = pd.read_csv(csv_name, usecols=usecols)
            self.logger.debug(f'Successfully read from {csv_name}')
            if column_name:
                return df[column_name]
            else:
                return df
        return None


if __name__ == '__main__':
    csv_helper = CSVHelper()
