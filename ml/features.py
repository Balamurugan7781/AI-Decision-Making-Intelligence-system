"""Feature Engineering to build a PD model.
   
This model builds a machine-learning ready database from the relational database

Objective:
Predict whether a approved loan will default or not. 

Target:
target_default = 1 if loan_status = 'defaulted' else 0

only pre-approval/application time features are used to predict the target variable.
Repayment history features are not used h ere because it results in data leakage.

"""
# Importing necessary libraries.....
 
import pandas as pd

from db.database import SessionLocal,engine
from db.models import Loan, Customer, LoanApplication

print(f"Database Engine: {engine}")

def predict_PD_model():
    """ This function is used to build a machine-learning ready database from the relational database. 
    It extracts features from the relational database and creates a pandas dataframe that can be used for training a machine learning model. 
    The function also creates a target variable that indicates whether a loan has defaulted or not.
    
    Returns pd.DataFrame: A pandas dataframe containing the features and target variable for the PD model.
    """
    session = SessionLocal()

    try:
        rows = (session.query(Customer,Loan, LoanApplication)
        .join(LoanApplication,Customer.customer_id  == LoanApplication.customer_id).join(Loan,LoanApplication.application_id == Loan.application_id).all())

        data=[]

        for customer,loan,loan_application in rows:
            # Financial Ratios.....
            #1st one : debt to income ratio....
            debt_to_income_ratio = customer.existing_debt/customer.annual_income if customer.annual_income > 0 else 0

            # 2nd one: loan_to_income_ratio.....
            loan_to_income_ratio = loan_application.requested_amount/customer.annual_income if customer.annual_income > 0 else 0

            # 3rd one: creating the target variable....
            target_variable = 1 if loan.loan_status == 'defaulted' else 0

            # Feature record.....
            results = {
                #Customer profile features.....
                'customer_id':customer.customer_id,
                'age':customer.age,
                'annual_income':customer.annual_income,
                'existing_debt':customer.existing_debt, 
                "credit_score":customer.credit_score,

                # Loan Application Status features.....
                'requested_amount':loan_application.requested_amount,
                'loan_term_months':loan_application.loan_term_months,
                "interest_rate":loan_application.interest_rate,

                # Engineered Features.....
                "debt_to_income_ratio":debt_to_income_ratio,
                "loan_to_income_ratio":loan_to_income_ratio,

                # Categorical features.....
                "employment_status":customer.employment_status,
                "region":customer.region,
                "segment":loan_application.segment,
                "channel":loan_application.channel,

                # Target variable.....
                "target_default":target_variable

            }

            data.append(results)
        df = pd.DataFrame(data)

        if df.empty:
            print("No data found in the database.")
            return df  # Return an empty DataFrame if no data is found
            
        # As we are having categorical features, we need to convert them into numerical features using one-hot encoding.....
        categorical_features = ['employment_status', 'region', 'segment', 'channel']
        df = pd.get_dummies(df, columns=categorical_features,drop_first=True,dtype=int)
        return df
        
    finally:
        session.close()



if __name__ == "__main__":
    df = predict_PD_model()
    print(df.head())
    print("\nPD Feature Dataset Created")
    print("=" * 50)

    print(f"Dataset Shape: {df.shape}")

    print("\nColumns:")
    print(df.columns.tolist())

    if not df.empty:
        print("\nTarget Distribution:")
        print(df["target_default"].value_counts())

        print("\nDefault Rate in Training Dataset:")
        default_rate = df["target_default"].mean() * 100
        print(f"{default_rate:.2f}%")

        df.to_csv("data/pd_training_dataset.csv", index=False)

        print("\nDataset saved to data/pd_training_dataset.csv")
    else:
        print("\nDataset is empty. Please run db.seed first.")