from listeners import Listener
from common.csv_helper import CSVHelper
from ml_worker import MLWorker
from common.conf import config
from common.logger import get_logger
import argparse
import time
import uuid


def generate_session_id():
    return uuid.uuid1().int % (10 ** 12)


def get_user_id(parser):
    parser.add_argument('--uid', action="store", dest="user_id")
    if parser.parse_args().user_id is not None:
        return int(parser.parse_args().user_id)
    else:
        return None


def __get_data_to_learn(df, dataset_header):
    return df[dataset_header[0]], df[dataset_header[1:]]


def __get_data_to_check(dataset_path):
    dataset_path_split = dataset_path.split('/')

    if len(dataset_path_split) < 2:
        dataset_name = dataset_path
    else:
        dataset_name = dataset_path_split[1]

    action_dict = listener.get_action_list(dataset_name)
    return CSVHelper().list_to_pd_dataframe(data_list=action_dict['list'], columns=action_dict['header'])


def __get_unique_users_list(users_list):
    for index, lst in enumerate(users_list):
        users_list[index] = list(set(lst))
    flat_list = [item for sublist in users_list for item in sublist]
    return list(set(flat_list))


def prepare_data_for_ml(dataset_path, dataset_header, logger):
    df = CSVHelper().read_from_csv(csv_name=dataset_path)
    try:
        user, data_to_learn = __get_data_to_learn(df, dataset_header)
    except IndexError as e:
        logger.error(f"Could't read file with base dataset. Error: {e}")
    else:
        data_to_check = __get_data_to_check(dataset_path)
        if data_to_check is not None:
            return data_to_check[dataset_header[1:]], data_to_learn, user
        else:
            return None, None, None


def make_identification(data_to_learn, user, data_to_check):
    if not data_to_check.empty:
        result_list = MLWorker().forest(data_to_learn, user, data_to_check).tolist()
        return max(set(result_list), key=result_list.count)


def detector(user_id):
    users_list = []
    user_id_result = []
    logger = get_logger('Detector')
    detect_types = {0: 'motion', 1: 'scroll', 2: 'keystroke'}

    for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
        data_to_check, data_to_learn, user = prepare_data_for_ml(dataset_path, dataset_header, logger)
        users_list.append(user.to_list())
        if data_to_check is not None:
            user_id_result.append(make_identification(data_to_learn, user, data_to_check))

    if user_id is None:
        print(f'User ID is not set. The most similar user is {max(set(user_id_result), key=user_id_result.count)}')
    else:
        if user_id in user_id_result:
            correct_type_ids = [index for index, value in enumerate(user_id_result) if value == user_id]
            print(f'OK. User {user_id}. Number of classifiers that confirm current user: {user_id_result.count(user_id)}. '
                  f'Detected by: {[detect_types[d_type] for d_type in correct_type_ids]}')
        else:
            print(f'Unknown user! User id result: {user_id_result}, user id: {repr(user_id)}')
            if user_id not in users_list:
                for dataset_path, dataset_header in zip(config.CSV_DATASETS.values(), config.CSV_HEADERS.values()):
                    CSVHelper().write_to_csv(csv_name=dataset_path, columns=dataset_header,
                                             actions_list=__get_data_to_check(dataset_path))

    listener.clear_action_list()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detector script')
    user_id = get_user_id(parser)
    session_id = generate_session_id()
    listener = Listener(user_id, session_id)
    listener.start_listening()
    print(f'Started listening. User ID: {user_id}, session ID: {session_id}')

    while True:
        time.sleep(config.SLEEP_TIME)
        detector(user_id)
