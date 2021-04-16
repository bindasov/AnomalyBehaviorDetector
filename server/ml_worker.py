from sklearn.ensemble import RandomForestClassifier


def forest(x_train, y_train, x_predict):
    forest = RandomForestClassifier(criterion='entropy', n_estimators=10, random_state=1, n_jobs=2)
    forest.fit(x_train, y_train)
    return forest.predict(x_predict)
