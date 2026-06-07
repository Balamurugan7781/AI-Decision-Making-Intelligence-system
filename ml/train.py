# Now for training purposes, we will use a simple logistic regression model from scikit-learn. We will train the model on the features we created and the target variable (loan approval).

from sklearn.linear_model import LogisticRegression
import joblib # this is for model saving and loading


def train_model(X, y):
    model = LogisticRegression()
    model.fit(X, y)


    joblib.dump(model, 'ml/loan_approval_model.pkl')
    return model