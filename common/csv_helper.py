import os
import pandas as pd


class CSVHelper:

    def __init__(self):
        pass

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
            row.to_csv(csv_name, index=False)
        else:
            row.to_csv(csv_name, mode='a', header=False, index=False)
