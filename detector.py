from listeners import Listener
from common.csv_helper import CSVHelper
from ml_worker import MLWorker
from common.conf import config
from common.logger import get_logger
import os
import argparse
import time


def generate_session_id():
    session_ids = []
    for csv_name in config.CSV_DATASETS.values():
        session_ids.extend(CSVHelper().read_from_csv(csv_name=csv_name, column_name='session'))
    if session_ids:
        return max(session_ids) + 1
    else:
        return 0


def generate_user_id():
    return abs(hash(os.getlogin())) % (10 ** 8)


def get_user_id():
    parser = argparse.ArgumentParser(description='Detector script')
    parser.add_argument('-uid', action="store", dest="user_id")
    args = parser.parse_args()
    return args.user_id


def prepare_data_for_ml(dataset_path, dataset_header, logger):
    df = CSVHelper().read_from_csv(csv_name=dataset_path)
    try:
        data_to_learn = df[dataset_header[1:]]
        user = df[dataset_header[0]]
    except AttributeError as e:
        logger.error(f"Could't read file with base dataset. Error: {e}")
    else:
        try:
            dataset_name = dataset_path.split('/')[1]
        except AttributeError:
            dataset_name = dataset_path
        action_dict = listener.get_action_list(action_type=dataset_name)
        data_to_check = CSVHelper().list_to_pd_dataframe(data_list=action_dict['list'],
                                                         columns=action_dict['header'])
        return data_to_check[dataset_header[1:]], data_to_learn, user


def make_identification(data_to_learn, user, data_to_check):
    dataset_ml_dict = {'motion.csv': MLWorker().knn,
                       'scroll.csv': MLWorker().forest,
                       'keystroke.csv': MLWorker().knn}

    if not data_to_check.empty:
        result_list = dataset_ml_dict['scroll.csv'](data_to_learn, user, data_to_check).tolist()
        # result_list = MLWorker().forest(data_to_learn, user, data_to_check).tolist()
        return max(set(result_list), key=result_list.count)


def detector():
    user_id_result = []
    data_to_check = None
    logger = get_logger('Detector')


    for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
        data_to_check, data_to_learn, user = prepare_data_for_ml(dataset_path, dataset_header, logger)
        user_id_result.append(make_identification(data_to_learn, user, data_to_check))

    if user_id in user_id_result:
        print(f'OK. Number of classifiers that confirm current user: {user_id_result.count(user_id)}')
        for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
            CSVHelper().write_to_csv(csv_name=dataset_path, columns=dataset_header, actions_list=data_to_check)
    else:
        print('Unknown user!')


if __name__ == '__main__':
    user_id = get_user_id()
    if user_id is None:
        user_id = generate_user_id()
    session_id = generate_session_id()
    listener = Listener(user_id, session_id)
    listener.start_listening()

    while True:
        time.sleep(config.SLEEP_TIME)
        detector()
