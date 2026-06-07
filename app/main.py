# Initialize the FastAPI app
from fastapi import FastAPI
from pydantic import BaseModel

from core.risk_engine import calculate_pd
from core.financial_engine import calculate_finances
from core.decision import make_decision

app = FastAPI()

# Define the input data model
class LoanApplication(BaseModel):
    loan_amount: float
    interest_rate: float
    income: float
    credit_score: int

@app.get("/")
def home():
    return{"message":"AI decision system for loan applications is running..."}

@app.post("/evaluate")
def evaluate_application(application: LoanApplication):
    print("REQUEST Received")
    pd = calculate_pd(application.credit_score, application.income)
    profit,loss,cost, net_profit = calculate_finances(pd, application.loan_amount, application.interest_rate)
    decision = make_decision(pd, net_profit)
    return {
        "probability_of_default": pd,
        "expected_profit": profit,
        "expected_loss": loss,
        "expected_cost": cost,
        "net_profit": net_profit,
        "decision": decision
    }