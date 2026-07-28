# Initialize the FastAPI app
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field

from ml.predict import predict_probability_of_default
# from core.risk_engine import calculate_pd
from core.financial_engine import evaluate_loan_financials
from core.policy_engine import evaluate_credit_policy
from core.decision import make_decision
from core.risk_adjustment import adjust_pd_for_term
from core.decision_audit_layer import create_decision_audit_record
from core.audit_repository import save_decision_audit_record
from core.lgd_logic_engine import estimate_lgd_from_collateral
# FASTAPI ......
app = FastAPI(title="AI FinTech Decision Intelligence System",description=("This is a FastAPIapplication that provides endpoint to expose the system . This system combines Probability of Default prediction, risk adjusted financial calculation with YAML policy based code" \
"   and deterministic code generation."), version="1.0.0",)

# Define the input data model
class LoanApplication(BaseModel):
    age: int = Field(..., description = "Age of the applicant")
    annual_income: float = Field(..., description = "Annual Income of the applicant")
    existing_debt: float = Field(..., description = "Existing Debt of the applicant")
    credit_score:int = Field(..., description = "Credit score of the applicant")
    requested_amount : int = Field(..., description = "Requested Loan Amount")
    loan_term_months: int = Field(..., description = "Loan term in months")
    interest_rate: float = Field(..., description = "Annual Interest rate in decimal format")
    is_secured: bool = Field(..., description= "Tells whether the loan application is collateral or not.")
    collateral_type: str =  Field(..., description="Type of collateral: none, property, gold, vehicle, deposit.")
    collateral_value: float = Field(default=0, description = "Estimated Collateral value.")

    employment_status: str = Field(..., description = "Employment status of the applicant")
    region: str
    segment:str
    channel:str

##########################################

# Health Check Endpoint......................

##########################################

# @app.get("/health")


@app.get("/")
def home() -> dict:
    return{"message":"AI decision system for loan applications is running...","status":"healthy"}

@app.get("/health")
def check() -> dict:
    return { "status": "ok", "service":"loan-decision-api"}


############################################

#MAIN Loan Evaluvation Endpoint......................

############################################

@app.post("/evaluate-loan")
def evaluate_loan(loan_application: LoanApplication) -> dict:
    "Evaluvate a loan application and return the final decision "

    try: 
        # Convert validated request into a dictionary.....
        application_data = loan_application.model_dump()
        collateral_coverage_ratio = loan_application.collateral_value / loan_application.requested_amount

        # now predict the probability of default......
        predict_pd = predict_probability_of_default(application_data=application_data)
        probability_of_default = predict_pd["probability_of_default"]
        risk_adjusted_result = adjust_pd_for_term(probability_of_default=probability_of_default,loan_term_months = loan_application.loan_term_months)
        adjusted_probability_of_default = risk_adjusted_result["adjusted_probability_of_default"]
        lgd_result = estimate_lgd_from_collateral(is_secured=loan_application.is_secured, collateral_type=loan_application.collateral_type,collateral_value=loan_application.collateral_value,requested_amount=loan_application.requested_amount)
        # now getting the financial data.......
        financial_results = evaluate_loan_financials(probability_of_default=adjusted_probability_of_default, loan_amount = loan_application.requested_amount,annual_interest_rate= loan_application.interest_rate, loan_term_months = loan_application.loan_term_months,loss_given_default=lgd_result["loss_given_default"], )

        # now trying to get the affordability ratios.......

        debt_to_income_ratio = loan_application.existing_debt/ loan_application.annual_income

        loan_to_income_ratio = loan_application.requested_amount / loan_application.annual_income

        # now trying to get the policy codes to compare with the loan application status....

        policy_codes = evaluate_credit_policy(probability_of_default = adjusted_probability_of_default, debt_to_income_ratio = debt_to_income_ratio, loan_to_income_ratio = loan_to_income_ratio, credit_score = loan_application.credit_score, expected_loss = financial_results["expected_loss"], risk_adjusted_income = financial_results["risk_adjusted_income"], risk_adjusted_net_profit = financial_results["risk_adjusted_net_profit"])

        # making decision keyword.....

        decision = make_decision(adjusted_probability_of_default, financial_result=financial_results, policy_result=policy_codes)

        # now checking audit records.....

        audit_record = create_decision_audit_record(application_data=application_data, prediction_result=predict_pd,lgd_result=lgd_result ,risk_adjustment_result=risk_adjusted_result, financial_result=financial_results, policy_result=policy_codes,decision_result=decision)
        # now ,saving the audit record.....
        saved_audit_id = save_decision_audit_record(audit_record=audit_record)
        # --------------------------------------------------
        # 6. API response
        # --------------------------------------------------

        return {
            "application": application_data,
            "prediction_result": adjusted_probability_of_default,
            "financial_result": financial_results,
            "risk_adjusted_result" : risk_adjusted_result, 
            "lgd_result": lgd_result,
            "policy_result": policy_codes,
            "decision_result": decision,
            "audit_record":audit_record,
            "audit_saved":True,
            "saved_audit_id":saved_audit_id,
            "summary": {
                "decision": decision["decision"],
                "raw_probability_of_default": probability_of_default,
                "adjusted_probability_of_default":adjusted_probability_of_default,
                "adjusted_probability_of_default_percent": round(adjusted_probability_of_default * 100,2),
                "risk_adjusted_net_profit": financial_results[
                    "risk_adjusted_net_profit"
                ],
                "policy_status": policy_codes["policy_status"],
                "primary_reason_codes": decision[
                    "primary_reason_codes"
                ],
                "passed_policy_rules": policy_codes.get(
                    "passed_rules",
                    [],
                ),
            },
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error