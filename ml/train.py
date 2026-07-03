# Now for training purposes, we will use a simple logistic regression model from scikit-learn. We will train the model on the features we created and the target variable (loan approval).

from pathlib import Path
import json

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
# importing metrics for model evaluvation..
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,roc_auc_score,classification_report,average_precision_score
import joblib # this is for model saving and loading
from sklearn.model_selection import train_test_split  # this is for splitting the dataset into training and testing....
from sklearn.preprocessing import StandardScaler  # this is for feature scaling....
from sklearn.pipeline import Pipeline  # this is for creating a pipeline for the model training and evaluation....

# now here I am calling the features from the features.py file to get the features and target variable for training the model....
from ml.features import predict_PD_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# MODEL_PATH = PROJECT_ROOT / "ml" / "loan_approval_model.pkl"

MODEL_DIRECTORY = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIRECTORY / "pd_model_pipeline.joblib"
METADATA_PATH = MODEL_DIRECTORY / "pd_model_metadata.json"

# Prepare Training data.....
RANDOM_STATE = 42
DECISION_THRESHOLD = 0.50
TEST_SIZE=0.20
RECALL_RATE = 0.30 # This line is kept for the purpose of removing the models which are having recall rate of less than 30 %.
"""def prepare_training_data(df: pd.DataFrame):
    # Separate features and target
    X = pd.drop(columns=['target_default'])
    y = pd['target_default']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test
    return model"""

#prepare the training data
def prepare_training_data(df: pd.DataFrame):
        # check if the target variable is present in the dataframe....
        if 'target_default' not in df.columns:
            raise ValueError("The target variable 'target_default' is not present in the dataframe.")
    
        # check oif there is values in the dataframe....
        if df.empty:
            raise ValueError("The dataframe is empty. Please provide a valid dataframe with data.")
    
        # check if there is more than 2 values in the target variable, if yes then raise an error as this is a binary classification problem....
        if df['target_default'].nunique() < 2:
            raise ValueError("The target variable 'target_default' must have at least two unique values for binary classification.")
    
        required_target = 'target_default'

        X = df.drop(columns=[required_target,'customer_id'])
        y = df[required_target].astype(int)

        return X,y


    # Model evaluvation.....
def model_evaluvation(model,X_test:pd.DataFrame, y_test:pd.Series,threshold:float=DECISION_THRESHOLD,):
    predicted_pb = model.predict_proba(X_test)[:,1]

    predicted_class = (predicted_pb >= threshold).astype(int)

    metrics = {"accuracy":round(accuracy_score(y_test,predicted_class),4),
                   "precision":round(precision_score(y_test,predicted_class),4),
                   "recall_default":round(recall_score(y_test,predicted_class),4),
                   "f1_score": round(f1_score(y_test,predicted_class),4),
                   "roc_curve":round(roc_auc_score(y_test,predicted_pb),4),
                   "pr_auc":round(average_precision_score(y_test,predicted_pb),4),
                   "decision_threshold":threshold}

        # Now taking confusion matrix.....
    matrix = confusion_matrix(y_test,predicted_class)
        
        # now taking report for the classes....
    report = classification_report(y_test,predicted_class,target_names=["non_default","default"],zero_division=0)

    return metrics, matrix,report

def train_and_evaluate_model(model_name,model,X_train,X_test,y_train,y_test):
    print(f"\nTraining {model_name}...")

    model.fit(X_train, y_train)

    metrics, matrix, report = model_evaluvation(
        model=model,
        X_test=X_test,
        y_test=y_test,
    )

    print(f"\n{model_name} results")
    print("=" * 50)

    for metric_name, value in metrics.items():
        print(f"{metric_name}: {value}")

    print("\nConfusion matrix:")
    print(matrix)

    print("\nClassification report:")
    print(report)

    return {
        "name": model_name,
        "model": model,
        "metrics": metrics,
        "confusion_matrix": matrix,
    }



def Logistic_Regression_model():
    return Pipeline(steps=[("scaler",StandardScaler()),("model",LogisticRegression(class_weight="balanced", max_iter=2000, random_state = 42))])

def Random_Forest_Model():
    return RandomForestClassifier(n_estimators=300,max_depth = 8, min_samples_split=10,min_samples_leaf=5,class_weight="balanced",random_state=RANDOM_STATE )

def train_pd_model():
    """ Train the PD model and save the baseline PD model """
     # now we are printing the PD dataset....
    print(f"Printing PD feature dataset: ")
    df = predict_PD_model()

    # checking the dataset shape and size....
    print(df.shape)
    print(df.size)

    # now focus on data splitting.....
    X,y = prepare_training_data(df)
    X_train, X_test, Y_train, Y_test = train_test_split(X,y, test_size =0.2,random_state = 43, stratify = y)

    print("\nTraining target distribution:")
    print(Y_train.value_counts())

    print("\nTesting target distribution:")
    print(Y_test.value_counts())



    # Building candidate models....
    logistic_model = Logistic_Regression_model()
    random_forest = Random_Forest_Model()


    # train and evaluvate candiate models....
    logistic_result = train_and_evaluate_model("Logistic Regression",logistic_model,X_train,X_test,Y_train,Y_test)
    # Now for Random Forest...
    random_forest_result = train_and_evaluate_model("Random Forest",random_forest,X_train,X_test,Y_train,Y_test)

    # let's take both model results...
    model_results = [logistic_result,random_forest_result]

    # taking the best results....
    best_result = max(model_results, key = lambda x:x["metrics"]["pr_auc"] and x["metrics"]["recall_default"]>RECALL_RATE)
    best_model_name = best_result["name"]
    best_model = best_result["model"]
    best_metrics = best_result["metrics"]

    print("\nBest Model Selected")
    print("=" * 50)
    print(f"Model: {best_model_name}")
    print(f"PR-AUC: {best_metrics['pr_auc']}")
    print(f"ROC-AUC: {best_metrics['roc_curve']}")
    print(f"Recall: {best_metrics['recall_default']}")
    print(f"Precision: {best_metrics['precision']}")
    # save the model and metdata...

    MODEL_DIRECTORY.mkdir(parents=True,exist_ok=True)

    joblib.dump(best_model,MODEL_PATH)

    # save model metadata to a JSON file
    metadata = {
        "selected_model": best_model_name,
        "selection_metric": "pr_auc",
        "model_purpose": "Probability of Default prediction",
        "target": "target_default",
        "feature_columns": X.columns.tolist(),
        "number_of_features": X.shape[1],
        "training_rows": len(X_train),
        "testing_rows": len(X_test),
        "default_rate_percent": round(
            float(y.mean() * 100),
            2,
        ),
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "decision_threshold": DECISION_THRESHOLD,
        "model_results": {
            result["name"]: result["metrics"]
            for result in model_results
        },
    }

    with open(METADATA_PATH,"w",encoding="utf-8") as metadata_file:
        json.dump(metadata,metadata_file, indent=4)

    print(f"\nModel saved to:")
    print(MODEL_PATH)

    print("\nModel metadata saved to:")
    print(METADATA_PATH)

    return best_model, best_metrics


if __name__ == "__main__":
    train_pd_model()