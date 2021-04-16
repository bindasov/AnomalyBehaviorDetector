import unittest
from common.helpers import DataHandler, CSVHelper
from common import config
from server.detector import Detector
from common.tasks import ClientTask

DATASET_PATH = '../research/mlcompare/'
DATASETS = ['motion', 'scroll', 'keystroke']


class TestServerMethods(unittest.TestCase):

    def test_detect_by_motion(self):
        user, training_data = DataHandler().prepare_training_data(DATASET_PATH + 'motion' + config.DATASET_EXTENSION,
                                                                  config.DATASETS['motion'])
        _, test_data = DataHandler().prepare_training_data('test_data/' + 'motion' + config.DATASET_EXTENSION,
                                                           config.DATASETS['motion'])
        result = Detector().make_identification(training_data, user, test_data)
        self.assertEqual(result, 5)

    def test_detect_by_scroll(self):
        user, training_data = DataHandler().prepare_training_data(DATASET_PATH + 'scroll' + config.DATASET_EXTENSION,
                                                                  config.DATASETS['scroll'])
        _, test_data = DataHandler().prepare_training_data('test_data/' + 'scroll' + config.DATASET_EXTENSION,
                                                           config.DATASETS['scroll'])
        result = Detector().make_identification(training_data, user, test_data)
        self.assertEqual(result, 5)

    def test_detect_by_keystroke(self):
        user, training_data = DataHandler().prepare_training_data(DATASET_PATH + 'keystroke' + config.DATASET_EXTENSION,
                                                                  config.DATASETS['keystroke'])
        _, test_data = DataHandler().prepare_training_data('test_data/' + 'keystroke' + config.DATASET_EXTENSION,
                                                           config.DATASETS['keystroke'])
        result = Detector().make_identification(training_data, user, test_data)
        self.assertEqual(result, 5)


class TestClientServerInteraction(unittest.TestCase):

    def test_client_to_server_mode_0(self):
        _, test_data = DataHandler().prepare_training_data('test_data/' + 'keystroke' + config.DATASET_EXTENSION,
                                                           config.DATASETS['keystroke'])
        res = ClientTask(config.SERVICE_ADDR).send_training_data('42', 'keystroke', CSVHelper().pd_dataframe_to_list(test_data))
        assert res, {'result': 0}

    def test_true_client_to_server_mode_1(self):
        _, test_data = DataHandler().prepare_training_data('test_data/' + 'keystroke' + config.DATASET_EXTENSION,
                                                           config.DATASETS['keystroke'])
        res = ClientTask(config.SERVICE_ADDR).authenticate_user('42', 'keystroke', test_data)
        assert res, {'result': 0, 'OK': True}

    def test_false_client_to_server_mode_1(self):
        _, test_data = DataHandler().prepare_training_data('test_data/' + 'keystroke' + config.DATASET_EXTENSION,
                                                           config.DATASETS['keystroke'])
        res = ClientTask(config.SERVICE_ADDR).authenticate_user('24', 'keystroke', test_data)
        assert res, {'result': 1, 'OK': False}


if __name__ == '__main__':
    unittest.main()
