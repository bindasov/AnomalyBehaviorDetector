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
from sklearn.metrics import confusion_matrix

AUC_POINTS = {'scroll.csv': {'Perceptron': [],
                             'DecisionTree': [],
                             'RandomForest': [],
                             'KNeighbors': [],
                             'Bayes': []},
              'motion.csv': {'Perceptron': [],
                             'DecisionTree': [],
                             'RandomForest': [],
                             'KNeighbors': [],
                             'Bayes': []},
              'keystroke.csv': {'Perceptron': [],
                                'DecisionTree': [],
                                'RandomForest': [],
                                'KNeighbors': [],
                                'Bayes': []}}


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


def prepare_report(classifier_name, y_test, classifier_output):
    y_pred = classifier_output[0]
    work_time = np.round(classifier_output[1], 2)
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    precision_macro_avg = toFixed(100 * report_dict['macro avg']['precision'], 2)
    recall_macro_avg = toFixed(100 * report_dict['macro avg']['recall'], 2)
    f1_macro_avg = toFixed(100 * report_dict['macro avg']['f1-score'], 2)
    accuracy = toFixed(100 * report_dict['accuracy'], 2)

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
    datasets_dict = {'scroll.csv': ['time', 'x', 'y', 'rotation'], 'motion.csv': ['x', 'y', 'time'],
                     'keystroke.csv': ['timepress', 'timerelease', 'keycode']}

    test_sizes = [0.2, 0.4, 0.6, 0.8, 0.9]

    for test_size in test_sizes:
        for datapath, value in datasets_dict.items():
            print('\nDataset: {}'.format(datapath))
            df = pd.read_csv('C:\\users\\binda\\downloads\\mlcompare\\' + datapath, delimiter=',')

            table = []
            table.append(['Classifier name', 'Test collection size', 'Accuracy (%)', 'Precision (%)',
                          'Recall (%)', 'F1-score (%)', 'Work Time (s)'])

            x = df[value]
            y = df['user']

            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=42)


            classifiers = {'Perceptron': try_perceptron, 'DecisionTree': try_decision_tree,
                           'RandomForest': try_random_forest, 'KNeighbors': try_knn, 'Bayes': try_bayes}

            for classifier_name, classifier_method in classifiers.items():
                classifier_res = classifier_method(x_train, x_test, y_train)
                table.append(prepare_report(classifier_name, y_test, classifier_res))

                conf_matrix = confusion_matrix(y_test, classifier_res[0])
                FP = conf_matrix.sum(axis=0) - np.diag(conf_matrix)
                FN = conf_matrix.sum(axis=1) - np.diag(conf_matrix)
                TP = np.diag(conf_matrix)
                TN = conf_matrix.sum() - (FP + FN + TP)
                fp = FP.sum()
                fn = FN.sum()
                tp = TP.sum()
                tn = TN.sum()
                print(f'FP: {fp}, FN: {fn}, TP: {tp}, TN: {tn}')
                x = fp / (tn + fp)
                y = tp / (tp + fn)
                AUC_POINTS[datapath][classifier_name].append((x, y))

            # table.append(prepare_report('Perceptron', y_test, perceptron_res))
            # table.append(prepare_report('DecisionTree', y_test, decision_tree_res))
            # table.append(prepare_report('RandomForest', y_test, random_forest_res))
            # table.append(prepare_report('KNeighbors', y_test, knn_res))
            # table.append(prepare_report('Bayes', y_test, bayes_res))
            print(tabulate(table))

    print(AUC_POINTS)


if __name__ == "__main__":
    main()
