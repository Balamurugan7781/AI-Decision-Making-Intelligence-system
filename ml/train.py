# Now for training purposes, we will use a simple logistic regression model from scikit-learn. We will train the model on the features we created and the target variable (loan approval).

from pathlib import Path
import json

import pandas as pd
from sklearn.linear_model import LogisticRegression
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

    # saving the pipeline....
    model_pipeline = Pipeline(steps=[("scaler",StandardScaler()),("model",LogisticRegression(class_weight="balanced", max_iter=2000, random_state = 42))])

    print("Training Logistic Regression PD model: ")

    model_pipeline.fit(X_train,Y_train)

    # Y_predictt = model_pipeline.predict_proba(X)

    metrics, matrix,report = model_evaluvation(model = model_pipeline, X_test = X_test, y_test = Y_test)

    # save the model and metdata...

    MODEL_DIRECTORY.mkdir(parents=True,exist_ok=True)

    joblib.dump(model_pipeline,MODEL_PATH)
    metadata = {"model_type":"LogisticRegression","purpose": "Probability of Default prediction","target": "target_default","feature_columns": X.columns.tolist(),
        "training_rows": len(X_train),"testing_rows": len(X_test),"default_rate_percent": round(y.mean()* 100,2),
        "class_weight": "balanced",
        "random_state": RANDOM_STATE,
        "metrics": metrics,
    }

    with open(METADATA_PATH,"w",encoding="utf-8") as metadata_file:
        json.dump(metadata,metadata_file, indent=4)

    print("\nPD Model Training Completed")
    print("=" * 55)

    print("\nEvaluation metrics:")

    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value}")

    print("\nConfusion matrix:")
    print(matrix)

    print("\nClassification report:")
    print(report)

    print(f"\nModel saved to:")
    print(MODEL_PATH)

    print("\nModel metadata saved to:")
    print(METADATA_PATH)

    return model_pipeline, metrics


if __name__ == "__main__":
    train_pd_model()