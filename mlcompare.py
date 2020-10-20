from sklearn.linear_model import Perceptron
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from tabulate import tabulate
import time


def prepare_report(classifier_name, y_test, classifier_output):
    y_pred = classifier_output[0]
    work_time = np.round(classifier_output[1], 2)
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    precision_macro_avg = 100 * np.around(report_dict['macro avg']['precision'], 3)
    recall_macro_avg = 100 * np.around(report_dict['macro avg']['recall'], 3)
    f1_macro_avg = 100 * np.around(report_dict['macro avg']['f1-score'], 3)
    accuracy = 100 * np.around(report_dict['accuracy'], 3)

    return [classifier_name, len(y_test), accuracy, precision_macro_avg, recall_macro_avg, f1_macro_avg, work_time]


def try_perceptron(x_train, x_test, y_train):
    ppn = Perceptron(max_iter=400, eta0=0.1, random_state=0)
    start = time.time()
    ppn.fit(x_train, y_train)
    end = time.time()
    return ppn.predict(x_test), end - start


def try_svm(x_train, x_test, y_train):
    svm = SVC(kernel='rbf', C=1.0, random_state=0)
    start = time.time()
    svm.fit(x_train, y_train)
    end = time.time()
    return svm.predict(x_test), end - start


def try_decision_tree(x_train, x_test, y_train):
    tree = DecisionTreeClassifier(criterion='entropy', max_depth=4, random_state=0)
    start = time.time()
    tree.fit(x_train, y_train)
    end = time.time()
    return tree.predict(x_test), end - start


def try_random_forest(x_train, x_test, y_train):
    forest = RandomForestClassifier(criterion='entropy',
                                    n_estimators=10,
                                    random_state=1,
                                    n_jobs=2)
    start = time.time()
    forest.fit(x_train, y_train)
    end = time.time()
    return forest.predict(x_test), end - start


def try_knn(x_train, x_test, y_train):
    knn = KNeighborsClassifier(n_neighbors=5, p=2, metric='minkowski')
    start = time.time()
    knn.fit(x_train, y_train)
    end = time.time()
    return knn.predict(x_test), end - start


def try_bayes(x_train, x_test, y_train):
    gnb = GaussianNB()
    start = time.time()
    gnb.fit(x_train, y_train)
    end = time.time()
    return gnb.predict(x_test), end - start


def main():
    datasets_dict = {'all.scroll.csv': ['time', 'x', 'y', 'rotation'], 'all.motion.csv': ['x', 'y', 'time'],
                     'all.keystroke.csv': ['timepress', 'timerelease', 'keycode']}

    for datapath, value in datasets_dict.items():
        print('\nDataset: {}'.format(datapath))
        df = pd.read_csv('initial_datasets/' + datapath, delimiter=',')

        print(df)

        table = []
        table.append(['Classifier name', 'Test collection size', 'Accuracy (%)', 'Precision (%)',
                      'Recall (%)', 'F1-score (%)', 'Work Time (s)'])

        x = df[value]
        y = df['user']
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.5, random_state=42)
        print(x_test)

        table.append(prepare_report('Perceptron', y_test, try_perceptron(x_train, x_test, y_train)))
        # table.append(prepare_report('SVM', y_test, try_svm(x_train, x_test, y_train)))
        table.append(prepare_report('DecisionTree', y_test, try_decision_tree(x_train, x_test, y_train)))
        table.append(prepare_report('RandomForest', y_test, try_random_forest(x_train, x_test, y_train)))
        table.append(prepare_report('KNeighbors', y_test, try_knn(x_train, x_test, y_train)))
        table.append(prepare_report('Bayes', y_test, try_bayes(x_train, x_test, y_train)))
        print(tabulate(table))


if __name__ == "__main__":
    main()
