"""
Probability of Default Inference Module

This module loads the saved PD model and predicts the
probability of default for a new loan application.
"""

from pathlib import Path
import json

import joblib
import pandas as pd


# ======================================================
# PATH CONFIGURATION
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIRECTORY = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIRECTORY / "pd_model_pipeline.joblib"
METADATA_PATH = MODEL_DIRECTORY / "pd_model_metadata.json"


# ======================================================
# MODEL LOADING
# ======================================================

def load_pd_model():
    """
    Load the trained Probability of Default model.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"PD model was not found at: {MODEL_PATH}. "
            "Run `python -m ml.train` first."
        )

    return joblib.load(MODEL_PATH)


def load_model_metadata() -> dict:
    """
    Load model metadata, including the expected feature columns.
    """

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata was not found at: {METADATA_PATH}. "
            "Run `python -m ml.train` first."
        )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8",
    ) as metadata_file:
        return json.load(metadata_file)


# ======================================================
# FEATURE PREPARATION
# ======================================================

def prepare_application_features(
    application_data: dict,
    expected_columns: list[str],
) -> pd.DataFrame:
    """
    Convert one loan application into the same feature structure
    used during model training.
    """

    required_fields = [
        "age",
        "annual_income",
        "existing_debt",
        "credit_score",
        "requested_amount",
        "loan_term_months",
        "interest_rate",
        "employment_status",
        "region",
        "segment",
        "channel",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in application_data
    ]

    if missing_fields:
        raise ValueError(
            f"Missing required application fields: {missing_fields}"
        )

    annual_income = float(application_data["annual_income"])
    existing_debt = float(application_data["existing_debt"])
    requested_amount = float(application_data["requested_amount"])

    if annual_income <= 0:
        raise ValueError(
            "annual_income must be greater than zero."
        )

    if requested_amount <= 0:
        raise ValueError(
            "requested_amount must be greater than zero."
        )

    debt_to_income_ratio = (
        existing_debt / annual_income
    )

    loan_to_income_ratio = (
        requested_amount / annual_income
    )

    feature_record = {
        "age": application_data["age"],
        "annual_income": annual_income,
        "existing_debt": existing_debt,
        "credit_score": application_data["credit_score"],
        "requested_amount": requested_amount,
        "loan_term_months": application_data["loan_term_months"],
        "interest_rate": application_data["interest_rate"],
        "debt_to_income_ratio": debt_to_income_ratio,
        "loan_to_income_ratio": loan_to_income_ratio,
        "employment_status": application_data["employment_status"],
        "region": application_data["region"],
        "segment": application_data["segment"],
        "channel": application_data["channel"],
    }

    feature_df = pd.DataFrame([feature_record])

    categorical_columns = [
        "employment_status",
        "region",
        "segment",
        "channel",
    ]

    feature_df = pd.get_dummies(
        feature_df,
        columns=categorical_columns,
        drop_first=False,
        dtype=int,
    )

    # Add missing training columns and remove unknown columns.
    feature_df = feature_df.reindex(
        columns=expected_columns,
        fill_value=0,
    )

    return feature_df


# ======================================================
# PD PREDICTION
# ======================================================

def predict_probability_of_default(
    application_data: dict,
) -> dict:
    """
    Predict the probability of default for one application.
    """

    model = load_pd_model()
    metadata = load_model_metadata()

    expected_columns = metadata.get("feature_columns")

    if not expected_columns:
        raise ValueError(
            "feature_columns are missing from model metadata."
        )

    features = prepare_application_features(
        application_data=application_data,
        expected_columns=expected_columns,
    )

    probability_of_default = float(
        model.predict_proba(features)[0, 1]
    )

    return {
        "probability_of_default": round(
            probability_of_default,
            4,
        ),
        "probability_of_default_percent": round(
            probability_of_default * 100,
            2,
        ),
        "model_name": metadata.get(
            "selected_model",
            "Unknown model",
        ),
        "model_threshold": metadata.get(
            "decision_threshold",
            0.50,
        ),
    }


# ======================================================
# LOCAL TEST
# ======================================================

if __name__ == "__main__":
    sample_application = {
        "age": 35,
        "annual_income": 60000,
        "existing_debt": 12000,
        "credit_score": 690,
        "requested_amount": 15000,
        "loan_term_months": 36,
        "interest_rate": 0.12,
        "employment_status": "employed",
        "region": "London",
        "segment": "prime",
        "channel": "web",
    }

    prediction = predict_probability_of_default(
        sample_application
    )

    print("\nPD Prediction")
    print("=" * 50)

    for key, value in prediction.items():
        print(f"{key}: {value}")